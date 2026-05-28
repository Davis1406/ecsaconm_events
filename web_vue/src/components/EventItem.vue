<template>
    <div class="flex flex-col p-3 sm:space-y-2 space-y-0 sm:space-x-0 border border-shuttle-gray-200 rounded-xl text-sm"
        :class="getRowClass(index)">
        <div class="flex sm:flex-row flex-col">
            <div class="text-bondi-blue-700 font-roboto-light text-xl">
                <router-link :to="{ name: 'AccessEvent', params: { id: event.id } }" class="flex-1">
                    {{ event.event }}
                </router-link>
            </div>
        </div>
        <div class="flex sm:flex-row flex-col">
            <div class="font-semibold sm:w-2/12 w-full">Date</div>
            <div class="text-abbey-400">:
                {{ formatDate(event.start_date) }} - {{ formatDate(event.end_date) }}
            </div>
        </div>
        <div class="flex sm:flex-row flex-col">
            <div class="font-semibold sm:w-2/12 w-full">Venue</div>
            <div class="text-abbey-400">:
                {{ event.location }}
            </div>
        </div>
        <div class="flex sm:flex-row flex-col">
            <div class="font-semibold sm:w-2/12 w-full">Country</div>
            <div class="text-abbey-400">:
                {{ event.country.country }}
            </div>
        </div>
        <div v-if="isRegistrationOpen" class="flex sm:flex-row flex-col">
            <div class="font-semibold sm:w-2/12 w-full">Registration</div>
            <div class="sm:w-10/12 w-full flex space-x-2 items-center" v-if="!isRegistered">
                <span :class="registrationStatusClass">
                    <div :class="registeredStatusClass">: ({{ registeredStatus }})</div>
                </span>
                <div class="flex items-center space-x-2">
                    <div>: Not registered</div>
                    <div>
                        <button @click="$emit('register', event.id)"
                            class="bg-mountain-meadow-800 rounded-2xl hover:bg-mountain-meadow-500 px-4 p-1 text-white-200 cursor-pointer">Register</button>
                    </div>
                </div>
            </div>
            <div v-else class="sm:w-10/12 w-full ite flex space-x-2 items-center">
                <div>: Registered</div>
                <!-- <div>
                    <button @click="$emit('deregister', event.id)"
                        class="bg-flamingo rounded-2xl hover:bg-flamingo-700 px-4 p-1 text-white-200 cursor-pointer">Cancel
                        Registeration</button>
                </div> -->
            </div>
        </div>
        <div class="flex sm:flex-row flex-col">
            <div class="font-semibold sm:w-2/12 w-full">Payment</div>
            <div v-if="isPaid" class="sm:w-10/12 w-full flex space-x-2 items-center">
                : Paid
            </div>
            <div class="sm:w-10/12 w-full flex space-x-2 items-center" v-else>
                <div class="flex items-center space-x-2">
                    <div>: Not paid</div>
                    <div>
                        <button @click="$emit('pay', event.id)"
                            class="bg-mountain-meadow-800 rounded-2xl hover:bg-mountain-meadow-500 px-4 p-1 text-white-200 cursor-pointer">Make
                            Payment</button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    components: {},
    props: {
        event: Object,
        index: Number,
        getRowClass: Function,
        getRegistrationStatus: Function,
        getRegisteredStatus: Function,
        getPaidStatus: Function
    },
    computed: {
        isRegistrationOpen() {
            console.log('This is some data from system', this.event);
            return this.getRegistrationStatus(this.event.registration_end_date) === 'open';
        },
        isRegistered() {
            return this.getRegisteredStatus(this.event.id);
        },
        registrationStatusClass() {
            return this.isRegistrationOpen ? 'text-mountain-meadow-900' : 'text-flamingo';
        },
        registeredStatusClass() {
            return this.isRegistered ? 'text-bondi-blue-600' : this.registrationStatusClass;
        },
        registeredStatus() {
            return this.isRegistered ? 'Registered' : this.isRegistrationOpen ? 'Open' : 'Closed';
        },
        isPaid() {
            return this.getPaidStatus();
        },
    },
    methods: {
        formatDate(dateString) {
            const date = new Date(dateString);
            return date.toLocaleString("en-UK", {
                day: "2-digit",
                month: "2-digit",
                year: "numeric",
            });
        },
    }
};
</script>
