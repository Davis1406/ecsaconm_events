<template>
    <form @submit.prevent="search" :class="widthClass">
        <input v-model="searchQuery" @input="queueSearch"
            class="mt-2 px-4 p-2 bg-white border shadow-sm border-ghost-600 placeholder-slate-400 focus:outline-none focus:border-athens-gray-500 focus:border-athens-gray-500 block w-full rounded-2xl sm:text-sm focus:ring-1"
            placeholder="Search..." />
    </form>
</template>
<script>
export default {
    name: "SearchComponent",
    props: {
        // Optional controlled value — lets the parent restore a search
        // (e.g. from the URL query) into the box. Not required; standalone
        // usage keeps its own internal state.
        value: { type: String, default: "" },
        // Optional width classes for the input (Tailwind). Default keeps the
        // original full-width-on-mobile / 4/12-on-desktop behaviour; pages
        // that want a narrower box override this.
        widthClass: { type: String, default: "sm:w-4/12 w-12/12" },
    },
    data() {
        return {
            searchQuery: this.value,
            debounceTimer: null,
        };
    },
    watch: {
        value(v) {
            if (this.searchQuery !== v) this.searchQuery = v;
        },
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
