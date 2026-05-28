<template>
  <div v-if="show" class="fixed inset-0 flex items-center justify-center z-50">
    <div class="flex flex-col border-2 border-bondi-blue-600 border-t-8 bg-white-100 rounded-xl shadow-lg w-4/12 z-50">
      <div class="flex flex-col items-center justify-center p-1">
        <SpinnerComponent v-if="isLoading" />
        <div v-else
          class="flex flex-col space-y-1 m-4 w-11/12 py-3 items-center justify-center border-4 border-bondi-blue-600">
          <div><img src="@/assets/images/logo.png" class="w-20 h-20"></div>
          <div v-if="participant.picture === ''"><img src="@/assets/images/profile.png"
              class="w-32 h-32 border border-bondi-blue-500"></div>
          <div v-else><img :src="getFullImageUrl(this.participant.picture)"
              class="w-32 h-32 border border-bondi-blue-500">
          </div>
          <div class="text-md px-2 font-semibold text-neon-carrot-600 items-center  text-center">{{ this.event.event
            }}</div>
          <div class="w-full flex-1 bg-bondi-blue-300 p-2 font-bold text-white-100 text-center">{{
            this.participant.participant_category }}</div>
          <div class="px-2">{{ this.participant.title }} {{ this.participant.firstname }} {{ this.participant.lastname
            }}
          </div>
          <div class="px-2">{{ this.participant.institution }}</div>
          <div class="px-2">{{ this.participant.country }}</div>
          <qrcode-vue :value="qrCodeValue" :size="100"></qrcode-vue>
        </div>
        <div class="flex flex-row space-x-4">
          <button type="submit"
            class="px-4 py-1 flex justify-center items-center space-x-3 text-white-100 bg-bondi-blue hover:bg-bondi-blue-400 rounded-2xl">
            Print <PrinterIcon class="w-6 h-6"></PrinterIcon> </button>
          <button @click="close"
            class="px-4 py-1 boder border-2 border-abbey-400 hover:border-abbey-200 rounded-2xl">Close</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
// import { updateItem } from "@/services/apiService";
import SpinnerComponent from "@/components/Spinner.vue";
import { PrinterIcon } from '@heroicons/vue/24/solid'
import QrcodeVue from 'qrcode.vue'

export default {
  components: {
    SpinnerComponent, PrinterIcon, QrcodeVue
  },
  data() {
    return {
      passwordData: {
        password: "",
      },
      isLoading: false,
      message: "",
      qrCodeValue: "http://example.com/userprofile/johndoe", // This should be dynamically generated based on user details
      apiUrl: import.meta.env.VITE_API_URL,
    };
  },


  props: {
    show: {
      type: Boolean,
      required: true,
    },
    participant: {
      type: Object,
      required: true,
    },
    event: {
      type: Object,
      required: true,
    },
  },

  methods: {
    async updatePassword() {
      this.isLoading = true;
    },
    close() {
      this.$emit("closed");
    },
    getFullImageUrl(picturePath) {
      return `${this.apiUrl}/${picturePath}`;
    }
  },
};
</script>
