<template>
    <div class="flex flex-col space-y-6 flex-1 items-center py-8">
        <div class="w-11/12 sm:w-8/12 space-y-6">
            <div class="text-2xl font-semibold text-abbey-500">Submit an Abstract</div>

            <!-- Login required notice -->
            <div v-if="!isLoggedIn"
                class="p-4 rounded-2xl text-sm bg-yellow-50 border border-yellow-300 text-yellow-800">
                You must be logged in to submit an abstract.
                <router-link :to="{ name: 'Login' }" class="ml-1 font-bold text-bondi-blue-500 hover:underline">
                    Log in here &rarr;
                </router-link>
            </div>

            <!-- Success message -->
            <div v-if="submitted"
                class="p-4 rounded-2xl text-sm bg-green-100 border border-green-400 text-green-800 flex items-start space-x-3">
                <div>
                    <p class="font-semibold">Abstract submitted successfully!</p>
                    <p class="mt-1">You will be notified by email once your abstract has been reviewed.</p>
                    <button @click="resetForm" class="mt-3 text-bondi-blue-500 hover:underline text-sm">
                        Submit another abstract &rarr;
                    </button>
                </div>
            </div>

            <!-- Error message -->
            <div v-if="submitError"
                class="p-4 rounded-2xl text-sm bg-red-100 border border-red-400 text-red-800">
                {{ submitError }}
            </div>

            <SpinnerComponent v-if="isLoading" />

            <form v-if="!submitted && isLoggedIn" @submit.prevent="submitAbstract" class="space-y-5">
                <div class="rounded-2xl border border-mercury-500 shadow-sm p-6 bg-white space-y-5">

                    <!-- Event selection -->
                    <div class="flex flex-col space-y-1">
                        <label class="text-sm font-medium text-abbey-500">
                            Event <span class="text-red-500">*</span>
                        </label>
                        <select v-model="form.event_id" required
                            class="border border-mercury-500 rounded-md px-3 py-2 text-sm text-abbey-500 focus:outline-none focus:border-bondi-blue-500">
                            <option :value="null" disabled>Select an event</option>
                            <option v-for="event in events" :key="event.id" :value="event.id">
                                {{ event.event }}
                            </option>
                        </select>
                    </div>

                    <!-- Title -->
                    <div class="flex flex-col space-y-1">
                        <label class="text-sm font-medium text-abbey-500">
                            Abstract Title <span class="text-red-500">*</span>
                        </label>
                        <input v-model="form.title" type="text" required
                            placeholder="Title of your abstract"
                            class="border border-mercury-500 rounded-md px-3 py-2 text-sm text-abbey-500 focus:outline-none focus:border-bondi-blue-500" />
                    </div>

                    <!-- Authors -->
                    <div class="flex flex-col space-y-1">
                        <label class="text-sm font-medium text-abbey-500">
                            Authors <span class="text-red-500">*</span>
                            <span class="font-normal text-xs opacity-60 ml-1">(comma separated)</span>
                        </label>
                        <input v-model="form.authors" type="text" required
                            placeholder="e.g. Jane Doe, John Smith"
                            class="border border-mercury-500 rounded-md px-3 py-2 text-sm text-abbey-500 focus:outline-none focus:border-bondi-blue-500" />
                    </div>

                    <!-- Institution -->
                    <div class="flex flex-col space-y-1">
                        <label class="text-sm font-medium text-abbey-500">Institution / Affiliation</label>
                        <input v-model="form.institution" type="text"
                            placeholder="e.g. Ministry of Health, University of Nairobi"
                            class="border border-mercury-500 rounded-md px-3 py-2 text-sm text-abbey-500 focus:outline-none focus:border-bondi-blue-500" />
                    </div>

                    <!-- Abstract Body -->
                    <div class="flex flex-col space-y-1">
                        <label class="text-sm font-medium text-abbey-500">
                            Abstract Body <span class="text-red-500">*</span>
                            <span class="font-normal text-xs opacity-60 ml-1">(max 300 words)</span>
                        </label>
                        <textarea v-model="form.abstract_text" rows="8" required
                            placeholder="Write or paste your abstract here..."
                            class="border border-mercury-500 rounded-md px-3 py-2 text-sm text-abbey-500 focus:outline-none focus:border-bondi-blue-500 resize-y"></textarea>
                        <p :class="wordCount > 300 ? 'text-red-500' : 'text-abbey-500 opacity-50'"
                            class="text-xs text-right">
                            {{ wordCount }} / 300 words
                            <span v-if="wordCount > 300" class="font-semibold ml-1">— over limit!</span>
                        </p>
                    </div>

                    <!-- Keywords -->
                    <div class="flex flex-col space-y-1">
                        <label class="text-sm font-medium text-abbey-500">
                            Keywords
                            <span class="font-normal text-xs opacity-60 ml-1">(optional, comma-separated)</span>
                        </label>
                        <input v-model="form.keywords" type="text"
                            placeholder="e.g. health systems, digital health, UHC"
                            class="border border-mercury-500 rounded-md px-3 py-2 text-sm text-abbey-500 focus:outline-none focus:border-bondi-blue-500" />
                    </div>
                </div>

                <div class="flex justify-end">
                    <button type="submit"
                        :disabled="isSubmitting || wordCount > 300"
                        class="px-6 py-2 rounded-md text-white bg-bondi-blue-500 hover:bg-bondi-blue-400 disabled:opacity-50 text-sm font-medium">
                        {{ isSubmitting ? 'Submitting...' : 'Submit Abstract' }}
                    </button>
                </div>
            </form>
        </div>
    </div>
</template>

<script>
import SpinnerComponent from "@/components/Spinner.vue";
import { fetchData, createItem } from "@/services/apiService";
import { useAuthStore } from "@/store/authStore";

export default {
    name: 'AbstractSubmission',
    components: {
        SpinnerComponent
    },
    data() {
        return {
            isLoading: true,
            isSubmitting: false,
            submitted: false,
            submitError: "",
            events: [],
            form: {
                event_id: null,
                title: "",
                authors: "",
                institution: "",
                abstract_text: "",
                keywords: "",
            }
        };
    },
    mounted() {
        // Pre-select event if eventId param provided
        const eventId = this.$route.params.eventId;
        if (eventId && eventId !== 'select') {
            this.form.event_id = parseInt(eventId) || null;
        }
        this.loadEvents();
    },
    setup() {
        const authStore = useAuthStore();
        const isLoggedIn = !!authStore.accessToken;
        const user = authStore.loginUser;
        return { isLoggedIn, user };
    },
    computed: {
        wordCount() {
            const text = this.form.abstract_text.trim();
            return text ? text.split(/\s+/).length : 0;
        }
    },
    methods: {
        async loadEvents() {
            try {
                const response = await fetchData("events", 1, 200, "");
                this.events = response.data || [];
            } catch (error) {
                console.error("Error fetching events:", error);
                this.events = [];
            } finally {
                this.isLoading = false;
            }
        },
        async submitAbstract() {
            if (!this.isLoggedIn) return;
            this.isSubmitting = true;
            this.submitError = "";
            try {
                const payload = {
                    event_id: this.form.event_id,
                    title: this.form.title,
                    abstract_text: this.form.abstract_text,
                    keywords: this.form.keywords || null,
                    institution: this.form.institution || null,
                    authors: this.form.authors,
                };
                await createItem("abstracts", payload);
                this.submitted = true;
            } catch (error) {
                console.error("Error submitting abstract:", error);
                this.submitError = error.response?.data?.detail || "Submission failed. Please try again.";
            } finally {
                this.isSubmitting = false;
            }
        },
        resetForm() {
            this.submitted = false;
            this.submitError = "";
            this.form = {
                event_id: null,
                title: "",
                authors: "",
                institution: "",
                abstract_text: "",
                keywords: "",
            };
        }
    }
}
</script>
