<template>
  <div v-if="show" class="fixed inset-0 flex items-center justify-center z-50 overflow-auto">
    <div
      class="flex flex-col border-2 pb-4 border-bondi-blue-500 border-t-8 bg-white-100 rounded-xl shadow-lg sm:w-5/12 w-11/12 max-h-[90vh] overflow-y-auto z-50">
      <div
        class="flex flex-row items-center justify-between font-bold text-lg text-abbey-500 border-b-2 p-4 px-6 border-bondi-blue-500">
        <div>Make Payment</div>
        <span title="Cancel Registration" class="p-1 border border-abbey-600 rounded-full cursor-pointer">
          <XCircleIcon class="w-5 h-5 text-abbey-800" @click="cancel" />
        </span>
      </div>
      <div class="flex flex-col space-y-4 p-4 px-6">
        <a class="sm:px-4 px-2 sm:py-2 py-1 m-4 rounded-md border  border-bondi-blue-500 text-bondi-blue-600 hover:text-bondi-blue-100  hover:bg-bondi-blue-600 text-center"
          href="https://ecsaconm.org/online-payment/" target="_blank">Click to open payment page</a>
      </div>
      <div class="flex flex-col space-y-4 px-8 text-center">
        Remember to send your payment confirmation to <span class="font-bold">info@ecsacon.org</span> for event receipt.
      </div>
    </div>
  </div>
</template>

<script>
import { XCircleIcon } from '@heroicons/vue/24/solid';
export default {
  components: {
    XCircleIcon
  },
  data() {
    return {
      isLoading: false,
      message: "",
    };
  },
  props: {
    show: {
      type: Boolean,
      required: true,
    },
  },
  methods: {
    cancel() {
      this.$emit("cancel");
    },
    watch: {
      show(val) {
        if (val) {
          document.body.style.overflow = 'hidden';
        } else {
          document.body.style.overflow = '';
        }
      }
    },
    mounted() {
      if (this.show) {
        document.body.style.overflow = 'hidden';
      }
    }
  },
};
</script>
