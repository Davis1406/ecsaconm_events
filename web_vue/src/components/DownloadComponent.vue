<template>
    <div class="relative inline-block text-left">
        <button @click="toggleDropdown"
            class="inline-flex justify-center w-full rounded-2xl border border-bondi-blue-600 bg-bondi-blue-500 hover:bg-bondi-blue-400 text-white-200 hover:text-white-500 shadow-sm px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
            Download
            <svg class="-mr-1 ml-2 h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor"
                aria-hidden="true">
                <path fill-rule="evenodd"
                    d="M5.293 9.293a1 1 0 011.414 0L10 12.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z"
                    clip-rule="evenodd" />
            </svg>
        </button>
        <div v-if="isOpen"
            class="dropdown-content right-0 mt-2 rounded-2xl shadow-lg bg-white ring-1 ring-black ring-opacity-5">
            <div class="py-1 flex flex-col" role="none">
                <button @click="participants"
                    class="block px-4 py-2 text-sm text-gray-700 border-b border-shuttle-gray-200" role="menuitem"
                    tabindex="-1" id="menu-item-1">Participants</button>
                <button @click="paid" class="block px-4 py-2 text-sm text-gray-700 border-b border-shuttle-gray-200"
                    role="menuitem" tabindex="-1" id="menu-item-1">Paid</button>
                <button @click="notPaid" class="block px-4 py-2 text-sm text-gray-700 border-b border-shuttle-gray-200"
                    role="menuitem" tabindex="-1" id="menu-item-1">Not paid</button>
                <button @click="attendance" class="block px-4 py-2 text-sm text-gray-700" role="menuitem" tabindex="-1"
                    id="menu-item-0">Attendance</button>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    data() {
        return {
            isOpen: false
        };
    },
    methods: {
        toggleDropdown() {
            this.isOpen = !this.isOpen;
        },
        participants() {
            this.$emit('participants');
            this.isOpen = false;
        },
        paid() {
            this.$emit('paid');
            this.isOpen = false;
        },
        notPaid() {
            this.$emit('notPaid');
            this.isOpen = false;
        },
        attendance() {
            this.$emit('attendance');
            this.isOpen = false;
        },
    }
};
</script>

<style scoped>
.dropdown-content {
    position: absolute;
    z-index: 10;
}
</style>
