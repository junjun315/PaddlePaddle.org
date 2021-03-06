# -*- coding: utf-8 -*-
#   Copyright (c) 2018 PaddlePaddle Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from django import template
from portal import menu_helper
from portal import portal_helper
from django.conf import settings

from portal import url_helper

register = template.Library()


@register.simple_tag(takes_context=True)
def apply_class_if_template(context, template_file_name, class_name):
    '''
    Function that returns 'active' if the current base template matches the passed in template name, otherwise return
    empty string.  This method is used to apply the "active" class to the root navigation links
    :param context:
    :param template_file_name:
    :return:
    '''
    if context.template.name == template_file_name:
        return class_name
    else:
        return ''

@register.simple_tag()
def server_start_time():
    """
    The tag returns the server start time set in settings.py
    This tag is mainly used to achieve expiring CSS files
    """
    return settings.SERVER_START_TIME


@register.inclusion_tag('_nav_bar.html', takes_context=True)
def nav_bar(context):
    """
    Build the navigation based on the current language.
    """
    current_lang_code = context.get('lang', context.request.LANGUAGE_CODE)
    # root_navigation = menu_helper.get_top_level_navigation(
    #     portal_helper.get_preferred_version(context.request),
    #     current_lang_code
    # )

    # TODO[thuan]: This is kinda hacky, need to find better way of removing visualdl docs from PPO
    # if 'visualdl' in root_navigation:
    #     root_navigation.pop('visualdl')

    # Since we default to english, we set the change lang toggle to chinese
    lang_label = u'中文'
    lang_link = '/change-lang?lang_code=zh'
    community_link = 'https://github.com/PaddlePaddle/Paddle/issues'
    default_docs_version = settings.DEFAULT_DOCS_VERSION

    if current_lang_code and current_lang_code == 'zh':
        lang_label = 'English'
        lang_link = '/change-lang?lang_code=en'
        community_link = 'https://ai.baidu.com/forum/topic/list/168'

    return _common_context(context, {
        # 'root_nav': root_navigation,
        'lang_def': { 'label': lang_label, 'link': lang_link },
        'community_link': community_link,
        'default_docs_version': default_docs_version,
    })


@register.inclusion_tag('_content_links.html', takes_context=True)
def content_links(context, content_id):
    current_lang_code = context.get('lang', context.request.LANGUAGE_CODE)
    docs_version = context.get('CURRENT_DOCS_VERSION', None)

    side_nav_content = menu_helper.get_content_navigation(
        context.request,
        content_id,
        current_lang_code,
        docs_version
    )

    return _common_context(context, {
        'side_nav_content': side_nav_content,
        'search_url': context.get('search_url', None),
        'current_lang_code': current_lang_code
    })


@register.inclusion_tag('_version_links.html', takes_context=True)
def version_links(context):
    versions = list(settings.VERSIONS)
    versions.reverse()

    return _common_context(context, {
        'versions':versions,
    })


def _common_context(context, additional_context):
    if not additional_context:
        additional_context = {}

    additional_context.update({
        'request': context.request,
        'template': context.template,
        'url_helper': context.get('url_helper', None),
        'settings': context.get('settings', None),
        'content_id': context.get('content_id', ''),
        'lang': context.get('lang', ''),
        'CURRENT_DOCS_VERSION': context.get('CURRENT_DOCS_VERSION', ''),
        'CURRENT_API_VERSION': context.get('CURRENT_API_VERSION', '')
    })

    return additional_context


@register.assignment_tag(takes_context=True)
def translation_assignment(context, leaf_node):
    return translation(context, leaf_node)


@register.simple_tag(takes_context=True)
def translation(context, leaf_node):
    """
    The leaf node of the menu.json could be a dictionary of a string
    When encountering a dictionary leaf node, load the value associated with the current language code
    """
    result = None

    if isinstance(leaf_node, basestring):
        result = leaf_node
    elif isinstance(leaf_node, dict):
        current_lang_code = context.get('current_lang_code', context.request.LANGUAGE_CODE)

        if current_lang_code in leaf_node:
            result = leaf_node[current_lang_code]

    return result


# We use this hack because there is no easy way for VDL app's template to be
# identified by the inclusion tag for nav_bar.
@register.assignment_tag(takes_context=True)
def setup_vdl_context(context):
    current_lang_code = context.get('lang', context.request.LANGUAGE_CODE)
    # root_navigation = menu_helper.get_top_level_navigation(
    #     portal_helper.get_preferred_version(context.request),
    #     current_lang_code
    # )

    # TODO[thuan]: This is kinda hacky, need to find better way of removing visualdl docs from PPO
    # if 'visualdl' in root_navigation:
    #     root_navigation.pop('visualdl')

    # Since we default to english, we set the change lang toggle to chinese
    lang_label = u'中文'
    lang_link = '/zh'

    if current_lang_code and current_lang_code == 'zh':
        lang_label = 'English'
        lang_link = '/en'

    return _common_context(context, {
        # 'root_nav': root_navigation,
        'lang_def': { 'label': lang_label, 'link': lang_link },
    })
