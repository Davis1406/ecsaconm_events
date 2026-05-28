<template>
    <div v-if="show" class="fixed inset-0 flex items-center justify-center z-50 overflow-auto">
        <div
            class="flex flex-col sm:w-10/12 w-11/12 max-h-[90vh] overflow-y-auto border-2 bg-bondi-blue-50 border-bondi-blue-500 border-t-8 z-50 rounded-xl shadow-lg">
            <div
                class="flex flex-row items-center justify-between font-bold text-lg text-abbey-500 border-b-2 p-4 px-6 border-bondi-blue-500">
                <div>Conference Badges</div>
                <span title="Cancel Registration" class="p-1 border border-abbey-600 rounded-full cursor-pointer">
                    <XCircleIcon class="w-5 h-5 text-abbey-800" @click="close" />
                </span>
            </div>

            <div>
                <button @click="generateNextPDF"
                    class="flex flex-row space-x-2 bg-abbey-500 hover:bg-abbey-300 text-white-400 py-2 px-4 rounded mb-4 m-4">
                    <DocumentIcon class="w-6 h-6"></DocumentIcon>
                    <span>Generate Next PDF ({{ remainingParticipants }}/{{ totalParticipants }} remaining)</span>
                </button>
            </div>

            <div id="badge-container">
                <div v-for="(participant, index) in paginatedParticipants" :key="index" class="badge-page">
                    <div class="border-4 border-ecsa-blue-500 flex flex-col justify-center text-center pb-10"
                        style="width: 50%; height: 100%;">
                        <!-- Badge content here -->
                        <div class="flex flex-row p-4 items-center justify-center space-x-4">
                            <div><img src="@/assets/images/logo.png" class="sm:h-20 h-12" /></div>
                            <div><img src="@/assets/images/lesotho.png" class="sm:h-20 h-12" /></div>
                            <div><img src="@/assets/images/ecsalogo.png" class="sm:h-20 h-12" /></div>
                        </div>
                        <div class="text-xl font-extrabold mb-3 pt-2">
                            <p>{{ participant.title }} <span class="uppercase">{{ participant.firstname }}</span> {{
                                participant.lastname }}</p>
                        </div>
                        <div class="flex flex-row bg-bondi-blue-500 font-bold text-white justify-center text-md pb-4">
                            <span class="uppercase">{{ participant.institution }}</span>
                        </div>
                        <div class="flex flex-row font-bold justify-center text-md pb-4">
                            <span>{{ participant.country }}</span>
                        </div>
                        <div class="flex flex-col items-center">
                            <div class="bg-bondi-blue-500 px-4 pb-4 font-bold text-white rounded-md text-md uppercase">
                                {{ participant.participant_category }}
                            </div>
                        </div>
                        <div class="flex justify-center pt-2">
                            <QRCodeVue :value="appUrl + '/#/user-event-status/' + participant.id + '/' + event_id + '/'"
                                :size="85" :color-dark="'#000000'" :color-light="'#ffffff'" />
                        </div>
                        <div class="font-3xl font-bold">ID #: {{ participant.id }}</div>
                        <div class="text-sm font-normal">www.ecsaconm.org</div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import html2pdf from "html2pdf.js";
import QRCodeVue from 'qrcode.vue';
import { XCircleIcon, DocumentIcon } from '@heroicons/vue/24/solid';
import Swal from "sweetalert2";

export default {
    components: {
        QRCodeVue, XCircleIcon, DocumentIcon
    },
    data() {
        return {
            badgesPerPDF: 30, // Limit of 30 per PDF
            startIndex: 0,
            appUrl: import.meta.env.VITE_API_URL
        };
    },
    computed: {
        paginatedParticipants() {
            return this.participants.slice(this.startIndex, this.startIndex + this.badgesPerPDF);
        },
        remainingParticipants() {
            return this.participants.length - this.startIndex;
        },
        totalParticipants() {
            return this.participants.length;
        }
    },
    props: {
        show: {
            type: Boolean,
            required: true
        },
        participants: {
            type: Array,
            required: true
        },
        event_id: {
            type: Number,
            required: true
        }
    },
    methods: {
        close() {
            this.$emit('close');
        },
        async generateNextPDF() {
            if (this.startIndex >= this.participants.length) {
                Swal.fire({
                    icon: "error",
                    title: "No Data",
                    text: "No more participants to print.",
                    confirmButtonText: "OK",
                });
                return;
            }

            const element = document.getElementById("badge-container");
            const opt = {
                margin: [0.2, 0.2],
                filename: `Conference_badges_${Math.floor(this.startIndex / this.badgesPerPDF) + 1}.pdf`,
                image: { type: "jpeg", quality: 0.98 },
                html2canvas: { scale: 2 },
                jsPDF: { unit: "in", format: "letter", orientation: "portrait" },
                pagebreak: { mode: ['css', 'legacy'] }
            };

            await html2pdf().from(element).set(opt).save();
            this.startIndex += this.badgesPerPDF;
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

<style scoped>
.badge-page {
    page-break-after: always;
    margin: 0.2in;
    padding-top: 1in;
    /* Fixed padding */
    padding-bottom: 1in;
    min-height: 10in;
    /* Ensure each badge page takes up the same height */
    max-height: 10in;
    /* Prevent content from stretching the page */
    display: flex;
    justify-content: center;
    align-items: center;
    flex-direction: column;
}

.badge-content {
    width: 100%;
    height: 8in;
    /* Set height to ensure consistent spacing inside badge */
    display: flex;
    flex-direction: column;
    justify-content: center;
    /* Center content vertically */
    align-items: center;
}

@media print {
    .badge-page {
        padding-top: 1in;
        padding-bottom: 1in;
        min-height: 10in;
        max-height: 10in;
    }
}
</style>
