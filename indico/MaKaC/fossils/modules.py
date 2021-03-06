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

from MaKaC.common.fossilize import IFossil
from MaKaC.common.Conversion import Conversion
from MaKaC.fossils.conference import ICategoryFossil, IConferenceMinimalFossil


class INewsItemFossil(IFossil):

    def getId(self):
        pass

    def getAdjustedCreationDate(self):
        pass
    getAdjustedCreationDate.convert = Conversion.datetime
    getAdjustedCreationDate.name = "creationDate"

    def getContent(self):
        pass
    getContent.name = "text"

    def getTitle(self):
        pass

    def getType(self):
        pass

    def getHumanReadableType(self):
        pass


class IObservedObjectFossil(IFossil):

    def getObject(self):
        """ Encapsulated Object - either Category or Conference """
    getObject.result = {"MaKaC.conference.Category": ICategoryFossil,
                        "MaKaC.conference.Conference": IConferenceMinimalFossil}

    def getWeight(self):
        """ Weight of the Observed Object """

    def getAdvertisingDelta(self):
        """ Time delta """
    getAdvertisingDelta.convert = lambda s: s.days
    getAdvertisingDelta.name = "delta"
