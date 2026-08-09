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
                            @click="sendReminders"
                            :disabled="isLoading || presenters.length === 0"
                            class="px-4 py-2 text-white rounded-md text-sm font-medium disabled:opacity-50"
                            style="background-color: rgb(254, 80, 103);">
                            {{ sendStatus || 'Send Reminders' }}
                        </button>
                    </div>
                </div>

                <SpinnerComponent v-if="isLoading" />

                <div v-else>
                    <div v-if="presenters.length === 0" class="p-4 text-center text-sm text-gray-500 italic">
                        All presenters have registered.
                    </div>

                    <div v-else class="rounded-md border border-gray-200 overflow-hidden">
                        <div class="flex bg-mercury-500 p-3 pt-2 pb-2 text-xs font-bold uppercase">
                            <div class="w-1/12 p-1">#</div>
                            <div class="w-3/12 p-1">Name</div>
                            <div class="w-3/12 p-1">Email</div>
                            <div class="w-3/12 p-1">Abstract</div>
                            <div class="w-2/12 p-1">Account</div>
                        </div>
                        <div
                            v-for="(p, idx) in presenters"
                            :key="p.email + idx"
                            class="flex p-3 pt-2 pb-2 text-sm items-center border-t border-gray-100 hover:bg-gray-50">
                            <div class="w-1/12 p-1 text-gray-400">{{ idx + 1 }}</div>
                            <div class="w-3/12 p-1 font-medium">{{ p.firstname }} {{ p.lastname }}</div>
                            <div class="w-3/12 p-1 text-gray-600 text-xs">{{ p.email }}</div>
                            <div class="w-3/12 p-1 text-gray-600 text-xs truncate">{{ p.abstract_title }}</div>
                            <div class="w-2/12 p-1">
                                <span
                                    :class="p.has_account ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'"
                                    class="px-2 py-1 rounded-full text-xs font-semibold">
                                    {{ p.has_account ? 'Yes' : 'No' }}
                                </span>
                            </div>
                        </div>
                    </div>

                    <div class="mt-3 text-sm text-gray-500">
                        Total unregistered presenters: <strong>{{ presenters.length }}</strong>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import HeaderView from '@/includes/Header.vue'
import SpinnerComponent from '@/components/Spinner.vue'
import { fetchData } from '@/services/apiService'

export default {
    name: 'AbstractNotificationsView',
    components: {
        HeaderView, SpinnerComponent
    },
    data() {
        return {
            headerTitle: 'Abstract Notifications',
            presenters: [],
            isLoading: true,
            sendStatus: '',
            eventId: 1
        }
    },
    mounted() {
        this.loadPreview()
    },
    methods: {
        async loadPreview() {
            this.isLoading = true
            this.sendStatus = ''
            try {
                const response = await fetchData(`abstracts/registration-reminder-preview?event_id=${this.eventId}`)
                this.presenters = response || []
            } catch (error) {
                console.error('Error loading preview:', error)
            } finally {
                this.isLoading = false
            }
        },
        async sendReminders() {
            this.isLoading = true
            this.sendStatus = 'Sending...'
            try {
                const response = await fetchData(`abstracts/send-registration-reminders?event_id=${this.eventId}`, 'POST')
                this.sendStatus = `Sent to ${response.sent || 0} presenters`
                setTimeout(() => { this.sendStatus = '' }, 3000)
            } catch (error) {
                console.error('Error sending reminders:', error)
                this.sendStatus = 'Error sending'
                setTimeout(() => { this.sendStatus = '' }, 3000)
            } finally {
                this.isLoading = false
            }
        }
    }
}
</script>
