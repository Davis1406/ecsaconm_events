<template>
    <div class="relative inline-block text-left">
        <button @click="toggleDropdown"
            class="inline-flex justify-center w-full rounded-md border border-shuttle-gray-200 bg-shuttle-gray-200 shadow-sm px-4 py-2 text-sm font-bold text-gray-700 hover:text-abbey-300 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
            Actions
            <svg class="-mr-1 ml-2 h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor"
                aria-hidden="true">
                <path fill-rule="evenodd"
                    d="M5.293 9.293a1 1 0 011.414 0L10 12.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z"
                    clip-rule="evenodd" />
            </svg>
        </button>
        <div v-if="isOpen"
            class="action-content right-0 mt-2 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5">
            <div class="py-1 w-full" role="none">
                <button @click="viewItem"
                    class="w-full px-4 py-1 text-sm text-gray-700 hover:text-bondi-blue-500 border-b border-shuttle-gray-200"
                    role="menuitem" tabindex="-1" id="menu-item-1">View</button>
                <button @click="editItem"
                    class="w-full px-4 py-1 text-sm text-gray-700 hover:text-bondi-blue-500 border-b border-shuttle-gray-200"
                    role="menuitem" tabindex="-1" id="menu-item-1">Edit</button>
                <button @click="deleteItem" class="w-full px-4 py-1 text-sm text-gray-700 hover:text-bondi-blue-500"
                    role="menuitem" tabindex="-1" id="menu-item-0">Delete</button>
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
        viewItem() {
            this.$emit('view');
            this.isOpen = false;
        },
        editItem() {
            this.$emit('edit');
            this.isOpen = false;
        },
        deleteItem() {
            this.$emit('delete');
            this.isOpen = false;
        },
    }
};
</script>

<style scoped>
.action-content {
    position: absolute;
    z-index: 10;
}
</style>
