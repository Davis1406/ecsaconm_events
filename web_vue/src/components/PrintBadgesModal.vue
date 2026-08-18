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
                    <div class="print-badge flex flex-col text-center overflow-hidden rounded-2xl"
                        style="width: 50%; height: 100%;">

                        <!-- Gradient header with dual logos -->
                        <div class="print-badge__header px-4 pt-4 pb-5 relative">
                            <div class="bg-white/95 rounded-xl px-3 py-2.5 flex items-stretch justify-center gap-3 shadow-sm">
                                <div class="flex-1 flex items-center justify-center">
                                    <img src="@/assets/images/ecsalogo.png" class="sm:h-14 h-10 object-contain" />
                                </div>
                                <div class="w-px bg-gray-200 self-stretch"></div>
                                <div class="flex-1 flex items-center justify-center">
                                    <img src="@/assets/images/logo.png" class="sm:h-14 h-10 object-contain" />
                                </div>
                            </div>
                        </div>

                        <!-- Body -->
                        <div class="bg-white px-4 pt-4 pb-3 -mt-3 rounded-t-2xl flex-1 flex flex-col">
                            <p class="text-lg font-extrabold text-gray-900 leading-tight">
                                {{ participant.title }} <span class="uppercase">{{ participant.firstname }}</span> {{ participant.lastname }}
                            </p>

                            <div class="flex justify-center mt-2">
                                <span class="print-badge__pill inline-block px-4 py-1 rounded-full text-white text-xs font-bold uppercase tracking-wide">
                                    {{ participant.participant_category }}
                                </span>
                            </div>

                            <p class="text-sm font-semibold text-gray-800 uppercase mt-3">{{ participant.institution }}</p>
                            <p class="text-xs text-gray-400 mt-0.5">{{ participant.country }}</p>

                            <div class="print-badge__divider my-3"></div>

                            <div class="flex flex-col items-center gap-1">
                                <QRCodeVue :value="appUrl + '/#/user-event-status/' + participant.id + '/' + event_id + '/'"
                                    :size="80" :color-dark="'#111827'" :color-light="'#ffffff'" />
                                <div class="text-xs font-semibold text-gray-400 mt-1">ID #: {{ participant.id }}</div>
                            </div>

                            <div class="text-xs font-medium mt-3" style="color: rgb(220,50,75);">www.ecsaconm.org</div>
                        </div>

                        <div class="print-badge__footer h-2"></div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
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

            // Lazy-load html2pdf (jspdf + html2canvas, ~700 KB) only when printing
            const { default: html2pdf } = await import("html2pdf.js");
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

.print-badge {
    border: 1px solid rgba(0,0,0,0.08);
    box-shadow: 0 4px 14px rgba(0,0,0,0.08);
}
.print-badge__header {
    background: linear-gradient(135deg, rgb(254,80,103) 0%, rgb(220,50,75) 100%);
}
.print-badge__pill {
    background: linear-gradient(135deg, rgb(254,80,103) 0%, rgb(220,50,75) 100%);
}
.print-badge__divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(220,50,75,0.25), transparent);
}
.print-badge__footer {
    background: linear-gradient(90deg, rgb(254,80,103) 0%, rgb(220,50,75) 100%);
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
