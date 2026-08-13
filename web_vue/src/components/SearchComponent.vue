<template>
    <form @submit.prevent="search" class="sm:w-4/12 w-12/12">
        <input v-model="searchQuery" @input="queueSearch"
            class="mt-2 px-4 p-2 bg-white border shadow-sm border-ghost-600 placeholder-slate-400 focus:outline-none focus:border-athens-gray-500 focus:border-athens-gray-500 block w-full rounded-2xl sm:text-sm focus:ring-1"
            placeholder="Search..." />
    </form>
</template>
<script>
export default {
    name: "SearchComponent",
    data() {
        return {
            searchQuery: "",
            debounceTimer: null,
        };
    },
    beforeUnmount() {
        clearTimeout(this.debounceTimer);
    },
    methods: {
        search() {
            clearTimeout(this.debounceTimer);
            this.$emit("search", this.searchQuery);
        },
        queueSearch() {
            clearTimeout(this.debounceTimer);
            this.debounceTimer = setTimeout(() => {
                this.$emit("search", this.searchQuery);
            }, 350);
        },
    },
};
</script>
