<template>
    <div v-if="show" class="fixed inset-0 flex items-center justify-center z-50 overflow-auto">
        <div
            class="flex flex-col border-2 border-bondi-blue-500 border-t-8 bg-white-100 rounded-xl shadow-lg sm:w-5/12 w-11/12 max-h-[90vh] overflow-y-auto z-50">
            <div
                class="flex flex-row items-center justify-between font-bold text-lg text-abbey-500 border-b-2 p-4 px-6 border-bondi-blue-500">
                <div>Bulk upload event participants</div>
                <span title="Cancel Registration" class="p-1 border border-abbey-600 rounded-full cursor-pointer">
                    <XCircleIcon class="w-5 h-5 text-abbey-800" @click="close" />
                </span>
            </div>
            <SpinnerComponent v-if="isLoading" />
            <div class="p-1 m-4 px-4 rounded-md text-sm bg-bondi-blue-200 border border-bondi-blue-400 text-bondi-blue-800"
                v-if="errorMsg">{{ errorMsg
                }}</div>
            <div class="p-1 m-4 px-4 rounded-md text-sm bg-mountain-meadow-100 border border-mountain-meadow-400 text-mountain-meadow-800"
                v-if="successMsg">
                {{ successMsg
                }}</div>
            <div class="flex flex-col p-6 space-y-4">
                <p>
                    [<a :href="excelFilePath" download="Participants.csv" class=" text-dodger-blue-600 italic">
                        Template file
                    </a>]
                </p>
                <input type="file" name="participants" @change="uploadEventParticipants">
            </div>
        </div>
    </div>
</template>

<script>
import { XCircleIcon } from '@heroicons/vue/24/solid';
import { createItem } from '@/services/apiService';
import SpinnerComponent from '@/components/Spinner.vue';

export default {
    components: { XCircleIcon, SpinnerComponent },
    data() {
        return {
            isLoading: false,
            file: null
        };
    },
    props: {
        show: {
            type: Boolean,
            required: true
        },
        eventID: {
            type: Number,
            required: true
        }
    },
    methods: {
        async uploadEventParticipants(e) {
            this.isLoading = true;
            this.file = e.target.files[0];
            if (!this.file) {
                alert("Please select a file!");
                this.isLoading = false;
                return;
            }
            const formData = new FormData();
            formData.append("file", this.file);
            formData.append("eventID", this.eventID); // Add eventID to FormData

            try {
                const response = await createItem("events/upload_participants/", formData);
                this.profile = response;
                this.isLoading = false;
                console.log("Data received", response);
                this.errorMsg = null;
                this.successMsg = "Succefully uploaded/amended event participants details"
            } catch (error) {
                this.successMsg = null
                this.errorMsg = error.response.data.detail
                this.isLoading = false;
            }
        },
        close() {
            this.$emit('close');
        },
    },
    computed: {
        excelFilePath() {
            return '/templates/Participants.csv';
        }
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
};
</script>
