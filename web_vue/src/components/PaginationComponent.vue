<template>
  <div class="flex flex-row items-center gap-3 py-4 text-sm">
    <button @click="prevPage" :disabled="currentPage === 1"
      class="px-4 py-2 rounded-2xl font-semibold text-white transition disabled:opacity-40 disabled:cursor-not-allowed"
      style="background-color: rgb(254,80,103);"
      :style="currentPage === 1 ? '' : 'background-color: rgb(254,80,103);'"
      @mouseover="e => { if (currentPage !== 1) e.target.style.backgroundColor = 'rgb(220,50,75)' }"
      @mouseleave="e => { e.target.style.backgroundColor = 'rgb(254,80,103)' }">
      &larr; Previous
    </button>
    <div class="font-medium text-gray-600">Page {{ currentPage }} of {{ totalPages }}</div>
    <button @click="nextPage" :disabled="currentPage === totalPages"
      class="px-4 py-2 rounded-2xl font-semibold text-white transition disabled:opacity-40 disabled:cursor-not-allowed"
      style="background-color: rgb(254,80,103);"
      @mouseover="e => { if (currentPage !== totalPages) e.target.style.backgroundColor = 'rgb(220,50,75)' }"
      @mouseleave="e => { e.target.style.backgroundColor = 'rgb(254,80,103)' }">
      Next &rarr;
    </button>
  </div>
</template>

<script>
export default {
  name: "PaginationComponent",
  props: {
    currentPage: Number,
    totalPages: Number,
  },
  methods: {
    prevPage() {
      if (this.currentPage > 1) {
        this.$emit("page-change", this.currentPage - 1);
      }
    },
    nextPage() {
      if (this.currentPage < this.totalPages) {
        this.$emit("page-change", this.currentPage + 1);
      }
    },
  },
};
</script>
