<template>
  <div class="space-y-1">

    <!-- MANAGEMENT section -->
    <p class="text-xs font-semibold uppercase tracking-widest text-gray-400 px-4 mt-4 mb-1">Management</p>

    <router-link
      v-if="permissionCodes.includes('ADMIN_DASHBOARD')"
      :to="{ name: 'Dashboard' }"
      class="flex flex-row items-center space-x-2 p-2 px-4 ml-4 rounded-l-xl transition"
      :class="$route.name === 'Dashboard' ? 'text-white' : 'text-gray-600 hover:text-gray-900 hover:bg-white'"
      :style="$route.name === 'Dashboard' ? 'background-color: rgb(254,80,103);' : ''">
      <RectangleGroupIcon class="h-5 w-5 flex-shrink-0" />
      <span>Dashboard</span>
    </router-link>

    <router-link
      v-if="permissionCodes.includes('VIEW_EVENT')"
      :to="{ name: 'Events' }"
      class="flex flex-row items-center space-x-2 p-2 px-4 ml-4 rounded-l-xl transition"
      :class="$route.name === 'Events' || $route.name === 'Event' ? 'text-white' : 'text-gray-600 hover:text-gray-900 hover:bg-white'"
      :style="$route.name === 'Events' || $route.name === 'Event' ? 'background-color: rgb(254,80,103);' : ''">
      <CalendarDaysIcon class="h-5 w-5 flex-shrink-0" />
      <span>Events</span>
    </router-link>

    <router-link
      v-if="permissionCodes.includes('VIEW_EVENT')"
      :to="{ name: 'Registrations' }"
      class="flex flex-row items-center space-x-2 p-2 px-4 ml-4 rounded-l-xl transition"
      :class="$route.name === 'Registrations' ? 'text-white' : 'text-gray-600 hover:text-gray-900 hover:bg-white'"
      :style="$route.name === 'Registrations' ? 'background-color: rgb(254,80,103);' : ''">
      <ClipboardDocumentListIcon class="h-5 w-5 flex-shrink-0" />
      <span>Registrations</span>
    </router-link>

    <router-link
      v-if="permissionCodes.includes('ADMIN_DASHBOARD')"
      :to="{ name: 'AttendanceConfirmation' }"
      class="flex flex-row items-center space-x-2 p-2 px-4 ml-4 rounded-l-xl transition"
      :class="$route.name === 'AttendanceConfirmation' ? 'text-white' : 'text-gray-600 hover:text-gray-900 hover:bg-white'"
      :style="$route.name === 'AttendanceConfirmation' ? 'background-color: rgb(254,80,103);' : ''">
      <CheckCircleIcon class="h-5 w-5 flex-shrink-0" />
      <span>Attendance</span>
    </router-link>

    <router-link
      v-if="permissionCodes.includes('VIEW_USER')"
      :to="{ name: 'Users' }"
      class="flex flex-row items-center space-x-2 p-2 px-4 ml-4 rounded-l-xl transition"
      :class="$route.name === 'Users' || $route.name === 'User' ? 'text-white' : 'text-gray-600 hover:text-gray-900 hover:bg-white'"
      :style="$route.name === 'Users' || $route.name === 'User' ? 'background-color: rgb(254,80,103);' : ''">
      <UsersIcon class="h-5 w-5 flex-shrink-0" />
      <span>Users</span>
    </router-link>

    <!-- SETTINGS section -->
    <p class="text-xs font-semibold uppercase tracking-widest text-gray-400 px-4 mt-4 mb-1">Settings</p>

    <router-link
      v-if="permissionCodes.includes('VIEW_USER')"
      :to="{ name: 'Configurations' }"
      class="flex flex-row items-center space-x-2 p-2 px-4 ml-4 rounded-l-xl transition"
      :class="$route.name === 'Configurations' ? 'text-white' : 'text-gray-600 hover:text-gray-900 hover:bg-white'"
      :style="$route.name === 'Configurations' ? 'background-color: rgb(254,80,103);' : ''">
      <Cog8ToothIcon class="h-5 w-5 flex-shrink-0" />
      <span>Configurations</span>
    </router-link>

    <router-link
      v-if="permissionCodes.includes('ADMIN_DASHBOARD')"
      :to="{ name: 'EmailTemplates' }"
      class="flex flex-row items-center space-x-2 p-2 px-4 ml-4 rounded-l-xl transition"
      :class="$route.name === 'EmailTemplates' ? 'text-white' : 'text-gray-600 hover:text-gray-900 hover:bg-white'"
      :style="$route.name === 'EmailTemplates' ? 'background-color: rgb(254,80,103);' : ''">
      <EnvelopeIcon class="h-5 w-5 flex-shrink-0" />
      <span>Email Templates</span>
    </router-link>

    <router-link
      v-if="permissionCodes.includes('ADMIN_DASHBOARD')"
      :to="{ name: 'Contacts' }"
      class="flex flex-row items-center space-x-2 p-2 px-4 ml-4 rounded-l-xl transition"
      :class="$route.name === 'Contacts' ? 'text-white' : 'text-gray-600 hover:text-gray-900 hover:bg-white'"
      :style="$route.name === 'Contacts' ? 'background-color: rgb(254,80,103);' : ''">
      <PhoneIcon class="h-5 w-5 flex-shrink-0" />
      <span>Contacts</span>
    </router-link>

    <!-- ACCOUNT section -->
    <p class="text-xs font-semibold uppercase tracking-widest text-gray-400 px-4 mt-4 mb-1">Account</p>

    <router-link
      :to="{ name: 'MyDashboard' }"
      class="flex flex-row items-center space-x-2 p-2 px-4 ml-4 rounded-l-xl transition"
      :class="$route.name === 'MyDashboard' || $route.name === 'MyAccountProfile' || $route.name === 'MyEvents' ? 'text-white' : 'text-gray-600 hover:text-gray-900 hover:bg-white'"
      :style="$route.name === 'MyDashboard' || $route.name === 'MyAccountProfile' || $route.name === 'MyEvents' ? 'background-color: rgb(254,80,103);' : ''">
      <UserCircleIcon class="h-5 w-5 flex-shrink-0" />
      <span>My Account</span>
    </router-link>

  </div>
</template>

<script>
import {
  RectangleGroupIcon, UsersIcon, Cog8ToothIcon,
  CalendarDaysIcon, UserCircleIcon, CheckCircleIcon,
} from '@heroicons/vue/24/solid'
import { ClipboardDocumentListIcon, EnvelopeIcon, PhoneIcon } from '@heroicons/vue/24/outline'
import { useAuthStore } from '@/store/authStore'

export default {
  name: 'SidebarView',
  components: {
    RectangleGroupIcon, UsersIcon, Cog8ToothIcon, CalendarDaysIcon,
    ClipboardDocumentListIcon, UserCircleIcon, EnvelopeIcon, PhoneIcon, CheckCircleIcon,
  },
  setup() {
    const authStore = useAuthStore()
    const permissions = authStore.permissions
    const permissionCodes = Array.isArray(permissions)
      ? permissions.map(p => (typeof p === 'string' ? p : p.permission_code))
      : []
    return { permissionCodes }
  },
}
</script>
