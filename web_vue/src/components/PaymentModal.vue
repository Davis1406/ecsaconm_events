<template>
  <div v-if="show" class="fixed inset-0 flex items-center justify-center z-50">
    <div class="flex flex-col border border-abbey-600 border-t-8 bg-white-100 rounded-xl shadow-lg w-5/12 z-50">
      <div class="font-bold text-lg text-abbey-500 border-b-1 p-4 px-6 space-y-4 border border-abbey-600">
        Payment confirmation
      </div>
      <div v-if="message" class="p-4 m-6 m-y-4 rounded-xl text-mountain-meadow-800 py-2 text bg-spray-600">
        {{ message }}
      </div>
      <form class="flex flex-col space-y-4 p-4 px-6" @submit.prevent="eventPayment" method="POST">
        <SpinnerComponent v-if="isLoading" />
        <label class="block">
          <span class="after:content-['*'] after:ml-0.5 after:text-red-500 block text-sm font-medium text-slate-700">
            Confirmation ID (Transaction ID)
          </span>
          <input type="text" v-model="paymentData.transaction_code"
            class="mt-2 px-3 py-3 bg-white border border-1 shadow-sm border-abbey-400 placeholder-slate-400 focus:outline-none focus:border-sky-500 focus:ring-sky-500 block w-full rounded-2xl sm:text-sm focus:ring-1"
            placeholder="Confirmation ID (Transaction id)" />
        </label>
        <div class="flex flex-row space-x-4">
          <button type="submit" class="mt-2 px-4 py-1 text-white-100 bg-bondi-blue hover:bg-bondi-blue-400 rounded-2xl">
            Save
          </button>
          <div @click="cancel"
            class="mt-2 px-4 py-1 boder border-2 border-abbey-400 hover:border-abbey-200 rounded-2xl">Close</div>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import { createItem } from "@/services/apiService";
import SpinnerComponent from "@/components/Spinner.vue";

export default {
  components: {
    SpinnerComponent
  },
  data() {
    return {
      paymentData: {
        transaction_code: "",
        user_id: "",
        event_id: "",
      },
      isLoading: false,
      message: "",
    };
  },
  props: {
    show: {
      type: Boolean,
      required: true,
    },
    userID: {
      type: Number,
      required: true,
    },
    eventID: {
      type: Number,
      required: true,
    }
  },

  methods: {

    async eventPayment() {
      this.paymentData.event_id = this.eventID;
      this.paymentData.user_id = this.userID;
      this.isLoading = true;
      try {
        const response = await createItem("events/add_event_payment/", this.paymentData
        );
        this.payment_data = response.data;
        this.isLoading = false;
        this.$emit("paid");
      } catch (error) {
        this.isLoading = false;
      }
    },
    cancel() {
      this.$emit("cancel");
    },
  },
};
</script>
