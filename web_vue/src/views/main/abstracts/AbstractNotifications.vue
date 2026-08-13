<template>
    <div class="flex flex-col space-y-4 flex-1">
        <HeaderView :headerTitle="headerTitle"></HeaderView>

        <div class="flex flex-col space-y-4">
            <div class="rounded-md border-2 border-white-600 shadow-sm bg-white p-4">
                <div class="flex sm:flex-row flex-col sm:justify-between sm:items-center items-start mb-4">
                    <div>
                        <h2 class="text-lg font-semibold text-abbey-500">Registration Reminders</h2>
                        <p class="text-sm text-gray-500">
                            Presenters with accepted abstracts who haven't registered yet.
                        </p>
                    </div>
                    <div class="flex space-x-2 mt-2 sm:mt-0">
                        <button
                            @click="loadPreview"
                            :disabled="isLoading"
                            class="px-4 py-2 bg-gray-100 text-gray-700 rounded-md text-sm font-medium hover:bg-gray-200 disabled:opacity-50">
                            Refresh
                        </button>
                        <button
                            @click="sendReminders('selected')"
                            :disabled="isLoading || presenters.length === 0 || selectedEmails.size === 0"
                            class="px-4 py-2 text-white rounded-md text-sm font-medium disabled:opacity-50"
                            style="background-color: rgb(254, 80, 103);">
                            {{ sendStatus || `Send to Selected (${selectedEmails.size})` }}
                        </button>
                        <button
                            @click="sendReminders('all')"
                            :disabled="isLoading || presenters.length === 0"
                            class="px-4 py-2 border rounded-md text-sm font-medium disabled:opacity-50"
                            style="border-color: rgb(254, 80, 103); color: rgb(254, 80, 103);">
                            Send to All ({{ presenters.length }})
                        </button>
                    </div>
                </div>

                <SpinnerComponent v-if="isLoading" />

                <div v-else>
                    <div v-if="presenters.length === 0" class="p-4 text-center text-sm text-gray-500 italic">
                        All presenters have registered.
                    </div>

                    <div v-else class="rounded-md border border-gray-200 overflow-hidden">
                        <div class="flex bg-mercury-500 p-3 pt-2 pb-2 text-xs font-bold uppercase items-center">
                            <div class="w-1/12 p-1 flex items-center gap-2">
                                <input
                                    type="checkbox"
                                    :checked="allSelected"
                                    @change="toggleSelectAll"
                                    class="w-4 h-4 rounded border-gray-300 cursor-pointer"
                                    style="accent-color: rgb(254, 80, 103);" />
                            </div>
                            <div class="w-2/12 p-1">Name</div>
                            <div class="w-3/12 p-1">Email</div>
                            <div class="w-3/12 p-1">Abstract</div>
                            <div class="w-1/12 p-1 text-center">Account</div>
                            <div class="w-1/12 p-1 text-center">Reminder Sent</div>
                            <div class="w-1/12 p-1 text-center">Last Sent</div>
                        </div>
                        <div
                            v-for="(p, idx) in presenters"
                            :key="p.email + idx"
                            class="flex p-3 pt-2 pb-2 text-sm items-center border-t border-gray-100 hover:bg-gray-50">
                            <div class="w-1/12 p-1 flex items-center">
                                <input
                                    type="checkbox"
                                    :checked="selectedEmails.has(p.email)"
                                    @change="toggleSelect(p.email)"
                                    class="w-4 h-4 rounded border-gray-300 cursor-pointer"
                                    style="accent-color: rgb(254, 80, 103);" />
                                <span class="text-gray-400 ml-2">{{ idx + 1 }}</span>
                            </div>
                            <div class="w-2/12 p-1 font-medium">{{ p.firstname }} {{ p.lastname }}</div>
                            <div class="w-3/12 p-1 text-gray-600 text-xs">{{ p.email }}</div>
                            <div class="w-3/12 p-1 text-gray-600 text-xs truncate">{{ p.abstract_title }}</div>
                            <div class="w-1/12 p-1 text-center">
                                <span
                                    :class="p.has_account ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'"
                                    class="px-2 py-1 rounded-full text-xs font-semibold">
                                    {{ p.has_account ? 'Yes' : 'No' }}
                                </span>
                            </div>
                            <div class="w-1/12 p-1 text-center">
                                <span
                                    v-if="p.reminder_sent"
                                    class="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-semibold bg-green-100 text-green-700">
                                    <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5"><path d="M5 13l4 4L19 7"/></svg>
                                    Yes
                                </span>
                                <span
                                    v-else
                                    class="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-semibold bg-red-50 text-red-600">
                                    <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5"><path d="M6 18L18 6M6 6l12 12"/></svg>
                                    No
                                </span>
                            </div>
                            <div class="w-1/12 p-1 text-center text-xs text-gray-500">
                                {{ p.last_reminder_at ? formatDate(p.last_reminder_at) : '—' }}
                            </div>
                        </div>
                    </div>

                    <div class="mt-3 flex justify-between items-center text-sm text-gray-500">
                        <div>
                            Total unregistered presenters: <strong>{{ presenters.length }}</strong>
                        </div>
                        <div>
                            Selected: <strong>{{ selectedEmails.size }}</strong>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import HeaderView from '@/includes/Header.vue'
import SpinnerComponent from '@/components/Spinner.vue'
import axios from 'axios'
import { useAuthStore } from '@/store/authStore'

export default {
    name: 'AbstractNotificationsView',
    components: {
        HeaderView, SpinnerComponent
    },
    setup() {
        const authStore = useAuthStore()
        return { accessToken: authStore.accessToken }
    },
    data() {
        return {
            headerTitle: 'Abstract Notifications',
            presenters: [],
            isLoading: true,
            sendStatus: '',
            eventId: 1,
            apiUrl: import.meta.env.VITE_API_URL,
            selectedEmails: new Set(),
        }
    },
    computed: {
        allSelected() {
            return this.presenters.length > 0 && this.presenters.every(p => this.selectedEmails.has(p.email))
        },
    },
    watch: {
        presenters() {
            this.selectedEmails = new Set()
        },
    },
    mounted() {
        this.loadPreview()
    },
    methods: {
        async loadPreview() {
            this.isLoading = true
            this.sendStatus = ''
            try {
                const res = await axios.get(`${this.apiUrl}/abstracts/registration-reminder-preview`, {
                    params: { event_id: this.eventId },
                    headers: { Authorization: `Bearer ${this.accessToken}` },
                })
                this.presenters = res.data || []
            } catch (error) {
                console.error('Error loading preview:', error)
            } finally {
                this.isLoading = false
            }
        },
        toggleSelect(email) {
            if (this.selectedEmails.has(email)) {
                this.selectedEmails.delete(email)
            } else {
                this.selectedEmails.add(email)
            }
            this.selectedEmails = new Set(this.selectedEmails)
        },
        toggleSelectAll() {
            if (this.allSelected) {
                this.selectedEmails = new Set()
            } else {
                this.selectedEmails = new Set(this.presenters.map(p => p.email))
            }
        },
        async sendReminders(mode) {
            const isAll = mode === 'all'
            const count = isAll ? this.presenters.length : this.selectedEmails.size
            if (count === 0) return

            this.isLoading = true
            this.sendStatus = 'Sending...'
            try {
                const payload = { event_id: this.eventId }
                if (!isAll) {
                    payload.selected_emails = Array.from(this.selectedEmails)
                }
                const res = await axios.post(`${this.apiUrl}/abstracts/send-registration-reminders`, payload, {
                    headers: { Authorization: `Bearer ${this.accessToken}` },
                })
                this.sendStatus = `Sent to ${res.data.sent || res.data.reminders_sent || 0} presenters`
                this.loadPreview()
                setTimeout(() => { this.sendStatus = '' }, 3000)
            } catch (error) {
                console.error('Error sending reminders:', error)
                this.sendStatus = 'Error sending'
                setTimeout(() => { this.sendStatus = '' }, 3000)
            } finally {
                this.isLoading = false
            }
        },
        formatDate(d) {
            if (!d) return '—'
            return new Date(d).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' })
        },
    }
}
</script>