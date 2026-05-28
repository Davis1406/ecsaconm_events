<template>
  <div class="min-h-screen flex items-start justify-center py-10 px-4">
    <SpinnerComponent v-if="isLoading" />

    <div v-else class="w-full max-w-md">

      <!-- Card -->
      <div class="bg-white rounded-2xl shadow-xl overflow-hidden">

        <!-- Pink top bar -->
        <div class="h-2" style="background-color: rgb(254,80,103);"></div>

        <!-- Logo header -->
        <div class="flex flex-col items-center pt-6 pb-4 px-6 border-b border-gray-100">
          <img src="@/assets/images/logo.png" alt="ECSACONM" class="h-14 object-contain mb-3" />
          <h1 class="text-base font-bold text-gray-800 text-center leading-snug">
            {{ event.event || 'Event Attendance' }}
          </h1>
          <p v-if="event.start_date" class="text-xs text-gray-400 mt-1">
            {{ formatDate(event.start_date) }}
            <span v-if="event.end_date"> – {{ formatDate(event.end_date) }}</span>
          </p>
        </div>

        <!-- Date strip -->
        <div class="flex items-center justify-center gap-2 px-6 py-3 text-xs font-medium text-white"
          style="background-color: rgb(254,80,103);">
          <svg class="w-3.5 h-3.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
          </svg>
          {{ formattedDate }}
        </div>

        <!-- Form body -->
        <div class="p-6 space-y-4">
          <p class="text-xs text-gray-400 text-center uppercase tracking-widest font-semibold">Confirm Attendance</p>
          <p class="text-sm text-gray-500 text-center">Enter your participant ID number to register your attendance for today.</p>

          <!-- Alerts -->
          <div v-if="errorMsg"
            class="flex items-center gap-2 p-3 rounded-xl text-sm text-red-700 bg-red-50 border border-red-200">
            <svg class="w-4 h-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
            {{ errorMsg }}
          </div>
          <div v-if="successMsg"
            class="flex items-center gap-2 p-3 rounded-xl text-sm text-green-700 bg-green-50 border border-green-200">
            <svg class="w-4 h-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
            </svg>
            {{ successMsg }}
          </div>

          <form @submit.prevent="confirmAttendance" class="space-y-3">
            <input
              v-model="attendanceConfirmData.user_id"
              type="text"
              placeholder="Participant ID #"
              class="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none transition"
              style="focus:border-color: rgb(254,80,103);"
            />
            <button
              type="submit"
              class="w-full py-3 rounded-xl text-white font-bold text-sm transition hover:opacity-90"
              style="background-color: rgb(254,80,103);">
              Confirm Attendance
            </button>
          </form>
        </div>

        <!-- Pink bottom bar -->
        <div class="h-2" style="background-color: rgb(254,80,103);"></div>
      </div>

      <!-- Footer note -->
      <p class="text-center text-xs text-gray-400 mt-4">www.ecsaconm.org</p>
    </div>
  </div>
</template>

<script>
import { createItem, fetchItem } from "@/services/apiService";
import SpinnerComponent from "@/components/Spinner.vue";

export default {
  name: "AttendanceView",
  components: { SpinnerComponent },
  data() {
    return {
      eventId: this.$route.params.eventId,
      event: {},
      isLoading: true,
      today: new Date(),
      attendanceConfirmData: {
        event_id: "",
        user_id: "",
      },
      errorMsg: null,
      successMsg: null,
    };
  },
  computed: {
    formattedDate() {
      return this.today.toLocaleDateString('en-US', {
        weekday: 'long', year: 'numeric', month: 'long', day: 'numeric',
      });
    },
  },
  mounted() {
    this.getEventAttendance();
  },
  methods: {
    async getEventAttendance() {
      try {
        const response = await fetchItem("events/event", this.eventId);
        this.event = response.event;
      } catch (error) {
        console.error("Error fetching event:", error);
      } finally {
        this.isLoading = false;
      }
    },
    async confirmAttendance() {
      this.attendanceConfirmData.event_id = this.eventId;
      this.errorMsg = null;
      this.successMsg = null;
      this.isLoading = true;
      try {
        await createItem("events/confirm_event_attendance/", this.attendanceConfirmData);
        this.successMsg = "Attendance confirmed successfully for today.";
        this.attendanceConfirmData.user_id = "";
        this.getEventAttendance();
      } catch (error) {
        this.errorMsg = error.response?.data?.detail || "Failed to confirm attendance.";
      } finally {
        this.isLoading = false;
      }
    },
    formatDate(dateString) {
      if (!dateString) return '';
      return new Date(dateString).toLocaleDateString("en-GB", {
        day: "2-digit", month: "short", year: "numeric",
      });
    },
  },
};
</script>
