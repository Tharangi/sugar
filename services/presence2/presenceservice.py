# Copyright (C) 2007, Red Hat, Inc.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import gobject
import dbus, dbus.service, dbus.glib
import buddyiconcache


_PRESENCE_SERVICE = "org.laptop.Sugar.Presence"
_PRESENCE_INTERFACE = "org.laptop.Sugar.Presence"
_PRESENCE_PATH = "/org/laptop/Sugar/Presence"


class NotFoundError(dbus.DBusException):
    def __init__(self):
        dbus.DBusException.__init__(self)
        self._dbus_error_name = _PRESENCE_INTERFACE + '.NotFound'


class PresenceService(dbus.service.Object):
    def __init__(self):
        self._next_object_id = 0

        self._buddies = {}      # key -> Buddy
        self._activities = {}   # activity id -> Activity

        self._icon_cache = buddyiconcache.BuddyIconCache()

        bus = dbus.SessionBus()
        self._bus_name = dbus.service.BusName(_PRESENCE_SERVICE, bus=bus)        

        # Our owner object
        if profile.get_nick_name():
            objid = self._get_next_object_id()
            self._owner = buddy.Owner(self, self._bus_name,
                                      objid, self._icon_cache)
            self._buddies[self._owner.get_key()] = self._owner
        else:
            self._owner = None

        dbus.service.Object.__init__(self, self._bus_name, _PRESENCE_PATH)

    def _get_next_object_id(self):
        """Increment and return the object ID counter."""
        self._next_object_id = self._next_object_id + 1
        return self._next_object_id

    @dbus.service.signal(_PRESENCE_INTERFACE, signature="o")
    def ActivityAppeared(self, activity):
        pass

    @dbus.service.signal(_PRESENCE_INTERFACE, signature="o")
    def ActivityDisappeared(self, activity):
        pass

    @dbus.service.signal(_PRESENCE_INTERFACE, signature="o")
    def BuddyAppeared(self, buddy):
        pass

    @dbus.service.signal(_PRESENCE_INTERFACE, signature="o")
    def BuddyDisappeared(self, buddy):
        pass

    @dbus.service.method(_PRESENCE_INTERFACE, out_signature="ao")
    def GetActivities(self):
        ret = []
        for act in self._activities.values():
            ret.append(act.object_path())
        return ret

    @dbus.service.method(_PRESENCE_INTERFACE, in_signature="s", out_signature="o")
    def GetActivityById(self, actid):
        if self._activities.has_key(actid):
            return self._activities[actid].object_path()
        raise NotFoundError("The activity was not found.")

    @dbus.service.method(_PRESENCE_INTERFACE, out_signature="ao")
    def GetBuddies(self):
        ret = []
        for buddy in self._buddies.values():
            ret.append(buddy.object_path())
        return ret

    @dbus.service.method(_PRESENCE_INTERFACE, in_signature="ay", out_signature="o")
    def GetBuddyByPublicKey(self, key):
        if self._buddies.has_key(key):
            return self._buddies[key].object_path()
        raise NotFoundError("The buddy was not found.")

    @dbus.service.method(_PRESENCE_INTERFACE, out_signature="o")
    def GetOwner(self):
        if not self._owner:
            raise NotFoundError("The owner was not found.")
        else:
            return self._owner.get_object_path()

    @dbus.service.method(_PRESENCE_INTERFACE, in_signature="sssa{sv}", out_signature="o")
    def ShareActivity(self, actid, atype, name, properties):
        raise NotImplementedError("not implemented yet")


def main():
    loop = gobject.MainLoop()
    ps = PresenceService()
    try:
        loop.run()
    except KeyboardInterrupt:
        print 'Ctrl+C pressed, exiting...'

if __name__ == "__main__":
    main()
