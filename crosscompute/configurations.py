import re
from fnmatch import fnmatch
from invisibleroads_macros.configuration import (
    RawCaseSensitiveConfigParser, unicode_safely)
from invisibleroads_macros.disk import are_same_path
from os import getcwd, walk
from os.path import abspath, basename, dirname, isabs, join
from pyramid.settings import asbool, aslist

from .exceptions import (
    ToolConfigurationNotFound, ToolNotFound, ToolNotSpecified)


TOOL_NAME_PATTERN = re.compile(r'crosscompute\s*(.*)')
ARGUMENT_NAME_PATTERN = re.compile(r'\{(.+?)\}')


def get_tool_definition_from_result(result_configuration_path):
    result_configuration_folder = dirname(abspath(result_configuration_path))
    result_configuration = RawCaseSensitiveConfigParser()
    result_configuration.read(result_configuration_path)
    tool_definition_configuration = dict(result_configuration.items(
        'tool_definition'))
    tool_configuration_path = tool_definition_configuration[
        'configuration_path']
    tool_name = tool_definition_configuration['tool_name']
    tool_definition = get_tool_definition_by_name_from_path(
        tool_configuration_path, tool_name)[tool_name]
    for k, v in result_configuration.items('result_arguments'):
        if k == 'target_folder':
            continue
        if (k.endswith('_path') or k.endswith('_folder')) and not isabs(v):
            v = join(result_configuration_folder, v)
        tool_definition[k] = v
    return tool_definition


def get_tool_definition(tool_folder=None, tool_name='', default_tool_name=''):
    if not tool_folder:
        tool_folder = getcwd()
    tool_definition_by_name = get_tool_definition_by_name_from_folder(
        tool_folder, default_tool_name)
    if not tool_definition_by_name:
        raise ToolConfigurationNotFound(
            'Tool configuration not found. Run this command in a folder '
            'with a tool configuration file or in a parent folder.')
    if len(tool_definition_by_name) == 1:
        return list(tool_definition_by_name.values())[0]
    if not tool_name:
        raise ToolNotSpecified('Tool not specified. %s' % (
            format_available_tools(tool_definition_by_name)))
    tool_name = tool_name or tool_definition_by_name.keys()[0]
    try:
        tool_definition = tool_definition_by_name[tool_name]
    except KeyError:
        raise ToolNotFound('Tool not found (%s). %s' % (
            tool_name, format_available_tools(tool_definition_by_name)))
    return tool_definition


def get_tool_definition_by_name_from_folder(
        tool_folder, default_tool_name=None):
    tool_definition_by_name = {}
    tool_folder = unicode_safely(tool_folder)
    default_tool_name = unicode_safely(default_tool_name)
    for root_folder, folder_names, file_names in walk(tool_folder):
        if are_same_path(root_folder, tool_folder):
            tool_name = default_tool_name or basename(tool_folder)
        else:
            tool_name = basename(root_folder)
        for file_name in file_names:
            if not fnmatch(file_name, '*.ini'):
                continue
            configuration_path = join(root_folder, file_name)
            tool_definition_by_name.update(
                get_tool_definition_by_name_from_path(
                    configuration_path,
                    default_tool_name=tool_name))
    return tool_definition_by_name


def get_tool_definition_by_name_from_path(
        tool_configuration_path, default_tool_name=None):
    tool_definition_by_name = {}
    tool_configuration_path = abspath(tool_configuration_path)
    tool_configuration = RawCaseSensitiveConfigParser()
    tool_configuration.read(tool_configuration_path)
    d = {
        u'configuration_path': tool_configuration_path,
        u'configuration_folder': dirname(tool_configuration_path),
    }
    for section_name in tool_configuration.sections():
        try:
            tool_name = TOOL_NAME_PATTERN.match(section_name).group(1).strip()
        except AttributeError:
            continue
        if not tool_name:
            tool_name = default_tool_name
        tool_definition = {
            unicode_safely(k): unicode_safely(v)
            for k, v in tool_configuration.items(section_name)}
        for key in tool_definition:
            if key.startswith('show_'):
                tool_definition[key] = asbool(tool_definition[key])
            elif key.endswith('.dependencies'):
                tool_definition[key] = aslist(tool_definition[key])
        tool_definition[u'tool_name'] = tool_name
        tool_definition[u'argument_names'] = parse_tool_argument_names(
            tool_definition.get('command_template', u''))
        tool_definition_by_name[tool_name] = dict(tool_definition, **d)
    return tool_definition_by_name


def format_available_tools(tool_definition_by_name):
    tool_count = len(tool_definition_by_name)
    return '%s available:\n%s' % (
        tool_count, '\n'.join(tool_definition_by_name))


def parse_tool_argument_names(command_template):
    return tuple(ARGUMENT_NAME_PATTERN.findall(command_template))
