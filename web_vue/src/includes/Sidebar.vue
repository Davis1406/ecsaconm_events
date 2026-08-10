<template>
  <nav class="flex flex-col gap-0.5 pt-1">

    <!-- ── Management ──────────────────────────────────────────────────── -->
    <p class="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant/60 px-3 pt-3 pb-1">Management</p>

    <router-link v-if="has('ADMIN_DASHBOARD')" :to="{ name: 'Dashboard' }" v-slot="{ isActive }" custom>
      <a @click.prevent="go('Dashboard')"
        class="nav-item" :class="isActive ? 'nav-item--active' : 'nav-item--idle'">
        <svg class="w-[18px] h-[18px] flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
          <rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/>
          <rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/>
        </svg>
        Dashboard
      </a>
    </router-link>

    <router-link v-if="has('VIEW_EVENT')" :to="{ name: 'Events' }" v-slot="{ isActive }" custom>
      <a @click.prevent="go('Events')"
        class="nav-item" :class="isEventActive ? 'nav-item--active' : 'nav-item--idle'">
        <svg class="w-[18px] h-[18px] flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
          <rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/>
        </svg>
        Events
      </a>
    </router-link>

    <router-link v-if="has('VIEW_EVENT')" :to="{ name: 'Registrations' }" v-slot="{ isActive }" custom>
      <a @click.prevent="go('Registrations')"
        class="nav-item" :class="isActive ? 'nav-item--active' : 'nav-item--idle'">
        <svg class="w-[18px] h-[18px] flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
          <path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/>
          <path d="M9 12h6M9 16h4"/>
        </svg>
        Registrations
      </a>
    </router-link>

    <router-link v-if="has('ADMIN_DASHBOARD')" :to="{ name: 'AttendanceConfirmation' }" v-slot="{ isActive }" custom>
      <a @click.prevent="go('AttendanceConfirmation')"
        class="nav-item" :class="isActive ? 'nav-item--active' : 'nav-item--idle'">
        <svg class="w-[18px] h-[18px] flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
          <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
        </svg>
        Attendance
      </a>
    </router-link>

    <router-link v-if="has('VIEW_USER')" :to="{ name: 'Users' }" v-slot="{ isActive }" custom>
      <a @click.prevent="go('Users')"
        class="nav-item" :class="isUserActive ? 'nav-item--active' : 'nav-item--idle'">
        <svg class="w-[18px] h-[18px] flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
          <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2M23 21v-2a4 4 0 00-3-3.87M16 3.13a4 4 0 010 7.75M9 7a4 4 0 110 8 4 4 0 010-8z"/>
        </svg>
        Users
      </a>
    </router-link>

    <!-- ── Abstracts ────────────────────────────────────────────────────── -->
    <p class="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant/60 px-3 pt-4 pb-1">Abstracts</p>

    <router-link v-if="has('ADMIN_DASHBOARD')" :to="{ name: 'Abstracts' }" v-slot="{ isActive }" custom>
      <a @click.prevent="go('Abstracts')"
        class="nav-item" :class="isAbstractActive ? 'nav-item--active' : 'nav-item--idle'">
        <svg class="w-[18px] h-[18px] flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
          <path d="M9 12h6M9 8h6M9 16h4M5 3h14a2 2 0 012 2v14a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2z"/>
        </svg>
        Submissions
      </a>
    </router-link>

    <!-- ── Settings ─────────────────────────────────────────────────────── -->
    <p class="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant/60 px-3 pt-4 pb-1">Settings</p>

    <router-link v-if="has('VIEW_USER')" :to="{ name: 'Configurations' }" v-slot="{ isActive }" custom>
      <a @click.prevent="go('Configurations')"
        class="nav-item" :class="isActive ? 'nav-item--active' : 'nav-item--idle'">
        <svg class="w-[18px] h-[18px] flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
          <path d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/>
          <circle cx="12" cy="12" r="3"/>
        </svg>
        Configurations
      </a>
    </router-link>

    <router-link v-if="has('ADMIN_DASHBOARD')" :to="{ name: 'EmailTemplates' }" v-slot="{ isActive }" custom>
      <a @click.prevent="go('EmailTemplates')"
        class="nav-item" :class="isActive ? 'nav-item--active' : 'nav-item--idle'">
        <svg class="w-[18px] h-[18px] flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
          <path d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
        </svg>
        Email Templates
      </a>
    </router-link>

    <router-link v-if="has('ADMIN_DASHBOARD')" :to="{ name: 'Contacts' }" v-slot="{ isActive }" custom>
      <a @click.prevent="go('Contacts')"
        class="nav-item" :class="isActive ? 'nav-item--active' : 'nav-item--idle'">
        <svg class="w-[18px] h-[18px] flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
          <path d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"/>
        </svg>
        Contacts
      </a>
    </router-link>

    <!-- ── Account ──────────────────────────────────────────────────────── -->
    <p class="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant/60 px-3 pt-4 pb-1">Account</p>

    <router-link :to="{ name: 'MyDashboard' }" v-slot="{ isActive }" custom>
      <a @click.prevent="go('MyDashboard')"
        class="nav-item" :class="isMyAccountActive ? 'nav-item--active' : 'nav-item--idle'">
        <svg class="w-[18px] h-[18px] flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
          <path d="M5.121 17.804A13.937 13.937 0 0112 16c2.5 0 4.847.655 6.879 1.804M15 10a3 3 0 11-6 0 3 3 0 016 0zm6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
        </svg>
        My Account
      </a>
    </router-link>

  </nav>
</template>

<script>
import { useAuthStore } from '@/store/authStore'

const ABSTRACT_ROUTES = ['Abstracts', 'Abstract', 'PresentationTemplates', 'UploadedPresentations']
const EVENT_ROUTES    = ['Events', 'Event', 'AddEvent', 'EditEvent']
const USER_ROUTES     = ['Users', 'User', 'AddUser', 'EditUser']
const MY_ACCOUNT      = ['MyDashboard', 'MyAccountProfile', 'MyEvents', 'MyEvent']

export default {
  name: 'SidebarView',
  setup() {
    const authStore = useAuthStore()
    const perms = authStore.permissions || []
    const permissionCodes = perms.map(p => (typeof p === 'string' ? p : p.permission_code))
    return { permissionCodes }
  },
  computed: {
    isAbstractActive() { return ABSTRACT_ROUTES.includes(this.$route.name) },
    isEventActive()    { return EVENT_ROUTES.includes(this.$route.name) },
    isUserActive()     { return USER_ROUTES.includes(this.$route.name) },
    isMyAccountActive(){ return MY_ACCOUNT.includes(this.$route.name) },
  },
  methods: {
    has(code) { return this.permissionCodes.includes(code) },
    go(name)  { this.$router.push({ name }) },
  },
}
</script>

<style scoped>
.nav-item {
  @apply flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-150 cursor-pointer;
}
.nav-item--idle {
  @apply text-on-surface-variant hover:bg-surface-container;
}
.nav-item--active {
  @apply text-white font-semibold;
  background-color: rgb(254, 80, 103);
}
</style>
