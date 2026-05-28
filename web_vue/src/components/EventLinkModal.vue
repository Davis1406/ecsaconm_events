<template>
    <div v-if="show" class="fixed inset-0 flex items-center justify-center z-50 overflow-auto">
        <div
            class="flex flex-col border-2 border-bondi-blue-500 border-t-8 bg-white-100 rounded-xl shadow-lg sm:w-5/12 w-11/12 max-h-[90vh] overflow-y-auto z-50">
            <div
                class="flex flex-row items-center justify-between font-bold text-lg text-abbey-500 border-b-2 p-4 px-6 border-bondi-blue-500">
                <div>Upload Event link</div>
                <span title="Cancel Registration" class="p-1 border border-abbey-600 rounded-full cursor-pointer">
                    <XCircleIcon class="w-5 h-5 text-abbey-800" @click="close" />
                </span>
            </div>
            <SpinnerComponent v-if="isLoading" />
            <div class="flex flex-col p-6 space-y-4">
                <form class="flex flex-col space-y-4 p-4 px-6" @submit.prevent="addEventLink" method="POST">
                    <label class="block">
                        <input type="text" v-model="linkData.link_name"
                            class="mt-2 px-3 py-3 bg-white border border-1 shadow-sm border-abbey-400 placeholder-slate-400 focus:outline-none focus:border-sky-500 focus:ring-sky-500 block w-full rounded-2xl sm:text-sm focus:ring-1"
                            placeholder="link title" required />
                    </label>
                    <label class="block">
                        <input type="text" v-model="linkData.link"
                            class="mt-2 px-3 py-3 bg-white border border-1 shadow-sm border-abbey-400 placeholder-slate-400 focus:outline-none focus:border-sky-500 focus:ring-sky-500 block w-full rounded-2xl sm:text-sm focus:ring-1"
                            placeholder="Link" required />
                    </label>
                    <label class="block">
                        <select name="participant_category"
                            class="mt-2 px-3 py-3 pr-4 bg-white border border-1 shadow-sm border-abbey-400 placeholder-slate-400 focus:outline-none focus:border-sky-500 focus:ring-sky-500 block w-full rounded-2xl sm:text-sm focus:ring-1"
                            v-model="linkData.access_level" required>
                            <option value="" disabled selected>--Access level--</option>
                            <option value="public">public</option>
                            <option value="private">private</option>
                        </select>
                    </label>
                    <div class="flex flex-row space-x-4">
                        <button type="submit"
                            class="mt-2 px-4 py-2 text-white-100 bg-bondi-blue hover:bg-bondi-blue-400 rounded-2xl">
                            Save
                        </button>
                    </div>
                </form>
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
            linkData: {
                link_name: "",
                link: "",
                access_level: "",
                event_id: "",
            },
            isLoading: false,
            message: "",
        };
    },
    props: {
        show: {
            type: Boolean,
            required: true
        },
        event_id: {
            type: Number,
            required: true
        }
    },
    methods: {
        async addEventLink() {
            this.isLoading = true;
            this.linkData.event_id = this.event_id;
            try {
                const response = await createItem("events/add_event_link/", this.linkData);
                this.link_data = response;
                this.isLoading = false;
                this.$emit('close');
            } catch (error) {
                console.error("Error adding an event link:", error);
                this.isLoading = false;
            }
        },
        close() {
            this.$emit('close');
        },
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
