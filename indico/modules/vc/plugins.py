# This file is part of Indico.
# Copyright (C) 2002 - 2015 European Organization for Nuclear Research (CERN).
#
# Indico is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 3 of the
# License, or (at your option) any later version.
#
# Indico is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Indico; if not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals
import re

from flask import render_template

from indico.util.decorators import classproperty
from indico.modules.vc.forms import VCPluginSettingsFormBase
from indico.modules.vc.models.vc_rooms import VCRoomLinkType
from indico.util.user import retrieve_principals, retrieve_principal
from indico.web.flask.templating import get_overridable_template_name
from indico.web.forms.base import FormDefaults


PREFIX_RE = re.compile('^vc_')


class VCPluginMixin(object):
    settings_form = VCPluginSettingsFormBase
    #: the :class:`IndicoForm` to use for the video conference room form
    vc_room_form = None
    #: default values to use

    def init(self):
        super(VCPluginMixin, self).init()
        if not self.name.startswith('vc_'):
            raise Exception('Video conference plugins must be named vc_*')

    def get_vc_room_form_defaults(self, event):
        return {}

    @property
    def service_name(self):
        return PREFIX_RE.sub('', self.name)

    @classproperty
    @classmethod
    def category(self):
        from indico.core.plugins import PluginCategory
        return PluginCategory.videoconference

    def render_form(self, **kwargs):
        """Renders the video conference room form
        :param kwargs: arguments passed to the template
        """
        tpl = get_overridable_template_name('manage_event_create_room.html', self, 'vc/')
        return render_template(tpl, **kwargs)

    def render_custom_create_button(self, **kwargs):
        tpl = get_overridable_template_name('create_button.html', self, 'vc/')
        return render_template(tpl, plugin=self, **kwargs)

    def render_info_box(self, vc_room, event_vc_room, event, **kwargs):
        tpl = get_overridable_template_name('info_box.html', self, 'vc/')
        moderator = retrieve_principal(vc_room.data.get('moderator'))
        phone_link = self.settings.get('vidyo_phone_link')
        link_type = event_vc_room.link_type
        if link_type == VCRoomLinkType.event:
            link_type = 'event'
        elif link_type == VCRoomLinkType.contribution:
            link_type = 'contribution'
        elif link_type == VCRoomLinkType.session:
            link_type = 'session'
        link_id = event_vc_room.link_id
        return render_template(tpl, plugin=self, event_vc_room=event_vc_room, event=event, vc_room=vc_room,
                               moderator=moderator, phone_link=phone_link, link_type=link_type, link_id=link_id,
                               **kwargs)

    def create_form(self, event, existing_vc_room=None, existing_event_vc_room=None):
        """Creates the video conference room form

        :param event: the event the video conference room is for
        :param existing_vc_room: a vc_room from which to retrieve data for the form
        :param \*\*kwargs: extra data to pass to the form if an existing vc room is passed
        :return: an instance of an :class:`IndicoForm` subclass
        """
        if existing_vc_room and existing_event_vc_room:
            kwargs = {
                'name': existing_vc_room.name,
                'linking': existing_event_vc_room.link_type.name,
            }

            if existing_event_vc_room.link_type != VCRoomLinkType.event:
                kwargs[existing_event_vc_room.link_type.name] = existing_event_vc_room.link_id

            defaults = FormDefaults(existing_vc_room.data, **kwargs)
        else:
            defaults = FormDefaults(self.get_vc_room_form_defaults(event))
        with self.plugin_context():
            return self.vc_room_form(prefix='vc-', obj=defaults, event=event, vc_room=existing_vc_room)

    def create_room(self, vc_room):
        raise NotImplementedError('Plugin must implement create_room()')

    def can_manage_vc_rooms(self, user, event):
        acl = self.settings.get('acl')
        if not acl:
            return True

        principals = retrieve_principals(acl)
        return any(principal.containsUser(user) for principal in principals)