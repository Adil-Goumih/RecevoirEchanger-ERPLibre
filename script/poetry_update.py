#!./.venv/bin/python
import os
import sys
import argparse
import logging
import toml
import ast
from collections import OrderedDict, defaultdict
from pathlib import Path
import iscompatible

new_path = os.path.normpath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(new_path)

from script import git_tool

_logger = logging.getLogger(__name__)


def get_config():
    """Parse command line arguments, extracting the config file name,
    returning the union of config file and command line arguments

    :return: dict of config file settings and command line arguments
    """
    config = git_tool.GitTool.get_project_config()

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='''\
        Update pip dependency in Poetry, clear pyproject.toml, search all dependencies
        from requirements.txt, search conflict version and generate a new list.
        Launch Poetry installation.
''',
        epilog='''\
'''
    )
    parser.add_argument('-d', '--dir', dest="dir", default="./",
                        help="Path of repo to change remote, including submodule.")
    parser.add_argument('-f', '--force', action="store_true",
                        help="Force create new list of dependency, ignore poetry.lock.")
    parser.add_argument('-v', '--verbose', action="store_true",
                        help="More information in execution, show stats.")
    args = parser.parse_args()
    return args


def get_lst_requirements_txt():
    return list(Path(".").rglob("requirements.[tT][xX][tT]"))


def get_lst_manifest_py():
    return list(Path(".").rglob("__manifest__.py"))


def combine_requirements(config):
    """
    Search all module and version in all requirements.txt file in this project.
    For each version, check compatibility and show warning with provenance file
    Generate requirements.txt to "./.venv/build_dependency.txt"
    :param config:
    :return:
    """
    priority_filename_requirement = "odoo/requirements.txt"
    lst_sign = ("==", "!=", ">=", "<=", "<", ">", ";")
    lst_requirements = []
    ignore_requirements = ["sys_platform == 'win32'", "python_version < '3.7'"]
    dct_requirements = defaultdict(set)
    lst_requirements_file = get_lst_requirements_txt()
    lst_requirements_with_condition = set()
    dct_special_condition = defaultdict(list)
    dct_requirements_module_filename = defaultdict(list)
    for requirements_filename in lst_requirements_file:
        with open(requirements_filename, 'r') as f:
            for a in f.readlines():
                b = a.strip()
                if not b or b[0] == "#":
                    continue

                # Regroup requirement
                for sign in lst_sign:
                    if sign in b:
                        # Exception, some time the sign ; can be first, just check
                        if sign != ";" and ";" in b and b.find(sign) > b.find(";"):
                            module_name = b[:b.find(";")]
                        else:
                            module_name = b[:b.find(sign)]
                        module_name = module_name.strip()
                        # Special condition for ";", ignore it
                        if ";" in b:
                            for ignore_string in ignore_requirements:
                                if ignore_string in b:
                                    break
                            if ignore_string in b:
                                break
                            lst_requirements_with_condition.add(module_name)
                            value = b[:b.find(";")].strip()
                            dct_special_condition[module_name].append(b)
                        else:
                            value = b
                        dct_requirements[module_name].add(value)
                        filename = str(requirements_filename)
                        dct_requirements_module_filename[value].append(filename)
                        break
                else:
                    dct_requirements[b].add(b)
                    filename = str(requirements_filename)
                    dct_requirements_module_filename[b].append(filename)
                lst_requirements.append(b)

    dct_requirements = get_manifest_external_dependencies(dct_requirements)

    dct_requirements_diff_version = {k: v for k, v in dct_requirements.items() if
                                     len(v) > 1}
    # dct_requirements_same_version = {k: v for k, v in dct_requirements.items() if
    #                                  len(v) == 1}
    if config.verbose:
        # TODO show total repo to compare lst requirements
        print(f"Total requirements.txt {len(lst_requirements_file)}, "
              f"total module {len(lst_requirements)}, "
              f"unique module {len(dct_requirements)}, "
              f"module with different version {len(dct_requirements_diff_version)}.")

    if dct_requirements_diff_version:
        # Validate compatibility
        for key, lst_requirement in dct_requirements_diff_version.items():
            result = None

            lst_version_requirement = []
            for requirement in lst_requirement:
                if ".*" in requirement:
                    requirement = requirement.replace(".*", "")
                result_number = iscompatible.parse_requirements(requirement)
                if not result_number:
                    # Ignore empty version
                    continue
                # Exception of missing feature in iscompatible
                # TODO support me in iscompatible lib
                no_version = result_number[0][1]
                if "b" in no_version:
                    result_number[0] = result_number[0][0], no_version[
                                                            :no_version.find("b")]
                elif not no_version[no_version.rfind(".") + 1:].isnumeric():
                    result_number[0] = result_number[0][0], no_version[
                                                            :no_version.rfind(".")]
                result_number = iscompatible.string_to_tuple(result_number[0][1])
                lst_version_requirement.append((requirement, result_number))
            # Check compatibility with all possibility
            is_compatible = True
            if len(lst_version_requirement) > 1:
                highest_value = sorted(lst_version_requirement, key=lambda tup: tup[1])[-1]
                for version_requirement in lst_version_requirement:
                    is_compatible &= iscompatible.iscompatible(version_requirement[0],
                                                               highest_value[1])
                if is_compatible:
                    result = highest_value[0]
                else:
                    # Find the requirements file and print the conflict
                    # Take the version from Odoo by default, else take the more recent
                    odoo_value = None
                    for version_requirement in lst_version_requirement:
                        filename_1 = dct_requirements_module_filename.get(
                            version_requirement[0])
                        if priority_filename_requirement in filename_1:
                            odoo_value = version_requirement[0]
                            break

                    if odoo_value:
                        str_result_choose = f"Select {odoo_value} because from Odoo"
                        result = odoo_value
                    else:
                        result = highest_value[0]
                        str_result_choose = f"Select highest value {result}"
                    str_versions = " VS ".join(
                        [f"{a[0]} from {dct_requirements_module_filename.get(a[0])}" for
                         a in lst_version_requirement])
                    print(f"WARNING - Not compatible {str_versions} - "
                          f"{str_result_choose}.")
            elif len(lst_version_requirement) == 1:
                result = lst_version_requirement[0][0]
            else:
                result = key

            if result:
                dct_requirements[key] = set((result,))
            else:
                print(f"Internal error, missing result for {lst_requirement}.")

    # Support ignored requirements
    lst_ignore = get_list_ignored()
    lst_ignored_key = []
    for key in dct_requirements.keys():
        for ignored in lst_ignore:
            if ignored == key:
                lst_ignored_key.append(key)
    for key in lst_ignored_key:
        del dct_requirements[key]

    with open("./.venv/build_dependency.txt", 'w') as f:
        f.writelines([f"{list(a)[0]}\n" for a in dct_requirements.values()])


def sorted_dependency_poetry(pyproject_filename):
    # Open pyproject.toml
    with open(pyproject_filename, 'r') as f:
        dct_pyproject = toml.load(f)

    # Get dependencies and update list, sorted
    # [tool.poetry.dependencies]
    tool = dct_pyproject.get("tool")
    if tool:
        poetry = tool.get("poetry")
        if poetry:
            dependencies = poetry.get("dependencies")
            python_dependency = ("python", dependencies.get("python", ''))
            lst_dependency = [(k, v) for k, v in dependencies.items() if k != "python"]
            lst_dependency = sorted(lst_dependency, key=lambda tup: tup[0])
            poetry["dependencies"] = OrderedDict([python_dependency] + lst_dependency)

    # Rewrite pyproject.toml
    with open(pyproject_filename, 'w') as f:
        toml.dump(dct_pyproject, f)


def delete_dependency_poetry(pyproject_filename):
    # Open pyproject.toml
    with open(pyproject_filename, 'r') as f:
        dct_pyproject = toml.load(f)

    # Get dependencies and update list, sorted
    # [tool.poetry.dependencies]
    tool = dct_pyproject.get("tool")
    if tool:
        poetry = tool.get("poetry")
        if poetry:
            dependencies = poetry.get("dependencies")
            python_dependency = ("python", dependencies.get("python", ''))
            poetry["dependencies"] = OrderedDict([python_dependency])

    # Rewrite pyproject.toml
    with open(pyproject_filename, 'w') as f:
        toml.dump(dct_pyproject, f)


def get_manifest_external_dependencies(dct_requirements):
    lst_manifest_file = get_lst_manifest_py()
    lst_dct_ext_depend = []
    for manifest_file in lst_manifest_file:
        with open(manifest_file, 'r') as f:
            contents = f.read()
            try:
                dct = ast.literal_eval(contents)
            except:
                _logger.error(f"File {manifest_file} contains error, skip.")
                continue
            ext_depend = dct.get("external_dependencies")
            if not ext_depend:
                continue
            python = ext_depend.get("python")
            if not python:
                continue
            for depend in python:
                requirement = dct_requirements.get(depend)
                if requirement:
                    requirement.add(depend)
                else:
                    dct_requirements[depend] = set([depend])

    return dct_requirements


def call_poetry_add_build_dependency():
    os.system("./script/poetry_add_build_dependency.sh")


def get_list_ignored():
    with open("./ignore_requirements.txt", 'r') as f:
        lst_ignore_requirements = [a.strip() for a in f.readlines()]
    return lst_ignore_requirements


def main():
    # repo = Repo(root_path)
    # lst_repo = get_all_repo()
    config = get_config()
    pyproject_toml_filename = f'{config.dir}pyproject.toml'

    delete_dependency_poetry(pyproject_toml_filename)
    combine_requirements(config)
    if config.force and os.path.isfile("./poetry.lock"):
        os.remove("./poetry.lock")
    call_poetry_add_build_dependency()
    sorted_dependency_poetry(pyproject_toml_filename)


if __name__ == '__main__':
    main()
