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

from datetime import datetime

from flask import session, request
from pytz import timezone
from werkzeug.exceptions import Forbidden, NotFound

from indico.modules.users import User
from indico.modules.users.views import WPUserDashboard, WPUser
from indico.modules.users.forms import UserDetailsForm, UserPreferencesForm, UserEmailsForm
from indico.util.date_time import timedelta_split
from indico.util.redis import suggestions
from indico.util.redis import client as redis_client
from indico.util.redis import write_client as redis_write_client
from MaKaC.common.fossilize import fossilize
from MaKaC.common.timezoneUtils import DisplayTZ
from MaKaC.services.implementation.user import UserComparator
from MaKaC.webinterface.rh.base import RHProtected


class RHUserBase(RHProtected):
    def _checkParams(self):
        if not session.user:
            return
        self.user = session.new_user
        if 'user_id' in request.view_args:
            self.user = User.get(request.view_args['user_id'])
            if self.user is None:
                raise NotFound('This user does not exist')

    def _checkProtection(self):
        RHProtected._checkProtection(self)
        if not self._doProcess:  # not logged in
            return
        if not self.user.can_be_modified(session.new_user):
            raise Forbidden('You cannot modify this user.')


class RHUserDashboard(RHUserBase):
    def _process(self):
        if redis_write_client:
            suggestions.schedule_check(self.user)

        tz = timezone(DisplayTZ().getDisplayTZ())
        hours, minutes = timedelta_split(tz.utcoffset(datetime.now()))[:2]
        return WPUserDashboard.render_template('dashboard.html', redis_enabled=bool(redis_client), timezone=unicode(tz),
                                               offset='{:+03d}:{:02d}'.format(hours, minutes), user=self.user,
                                               categories=self.user.getRelatedCategories(),
                                               suggested_categories=self.user.getSuggestedCategories())


class RHUserAccount(RHUserBase):
    def _process(self):
        form = UserDetailsForm()
        return WPUser.render_template('account.html', user=self.user, form=form)


class RHUserPreferences(RHUserBase):
    def _process(self):
        form = UserPreferencesForm()
        return WPUser.render_template('preferences.html', user=self.user, form=form)


class RHUserFavorites(RHUserBase):
    def _process(self):
        favorite_categs = [dict(id=c.getId(), title=c.getTitle()) for c in
                           self.user.getLinkTo('category', 'favorite')]
        users = self.user.getPersonalInfo().getBasket().getUsers().values()
        fossilizedUsers = sorted(fossilize(users), cmp=UserComparator.cmpUsers)
        favorite_users = fossilizedUsers
        return WPUser.render_template('favorites.html', user=self.user, favorite_categs=favorite_categs,
                                      favorite_users=favorite_users)


class RHUserEmails(RHUserBase):
    def _process(self):
        form = UserEmailsForm()
        emails = []
        return WPUser.render_template('emails.html', user=self.user, form=form, emails=emails)
