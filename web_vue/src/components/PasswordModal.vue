<template>
  <div v-if="show" class="fixed inset-0 flex items-center justify-center z-50 overflow-auto">
    <div
      class="flex flex-col border-2 border-bondi-blue-500 border-t-8 bg-white-100 rounded-xl shadow-lg sm:w-5/12 w-11/12 max-h-[90vh] overflow-y-auto z-50">
      <div
        class="flex flex-row items-center justify-between font-bold text-lg text-abbey-500 border-b-2 p-4 px-6 border-bondi-blue-500">
        <div>New Password</div>
        <span title="Cancel Registration" class="p-1 border border-abbey-600 rounded-full cursor-pointer">
          <XCircleIcon class="w-5 h-5 text-abbey-800" @click="close" />
        </span>
      </div>

      <div v-if="message" class="p-4 m-6 m-y-4 rounded-xl text-mountain-meadow-800 py-2 text bg-spray-600">
        {{ message }}
      </div>
      <form class="flex flex-col space-y-4 p-4 px-6" @submit.prevent="updatePassword" method="POST">
        <SpinnerComponent v-if="isLoading" />
        <label class="block">
          <span class="after:content-['*'] after:ml-0.5 after:text-red-500 block text-sm font-medium text-slate-700">
            New password
          </span>
          <input type="text" v-model="passwordData.password"
            class="mt-2 px-3 py-3 bg-white border border-1 shadow-sm border-abbey-400 placeholder-slate-400 focus:outline-none focus:border-sky-500 focus:ring-sky-500 block w-full rounded-2xl sm:text-sm focus:ring-1"
            placeholder="New password" required />
        </label>
        <div class="flex flex-row space-x-4">
          <button type="submit" class="mt-2 px-4 py-2 text-white-100 bg-bondi-blue hover:bg-bondi-blue-400 rounded-2xl">
            Save
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import { updateItem } from "@/services/apiService";
import SpinnerComponent from "@/components/Spinner.vue";
import { XCircleIcon } from '@heroicons/vue/24/solid';

export default {
  components: {
    SpinnerComponent, XCircleIcon
  },
  data() {
    return {
      passwordData: {
        password: "",
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
    user_id: {
      type: Number,
      required: true,
    },
  },

  methods: {

    async updatePassword() {
      this.isLoading = true;
      try {
        const response = await updateItem("users/reset_password", this.user_id, this.passwordData
        );
        this.user_data = response.data;
        this.isLoading = false;
        this.$emit("password-set");
        this.message = "Password updated successfully";
      } catch (error) {
        this.isLoading = false;
      }
    },
    close() {
      this.$emit("closed");
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
  },
};
</script>
