<template>
    <div class="sm:flex sm:flex-row flex flex-col flex-1 justify-center items-center">
        <div class="sm:w-7/12 w-11/12 flex flex-col sm:space-y-4 space-y-2 rounded-md p-8 bg-ghost-300">
            <div class="sm:font-roboto-thin font-roboto text-ghost-900 sm:text-4xl text-xl">Sign up</div>
            <div v-if="message" class="text-great-blue-400">{{ message }}</div> <!-- Display error message -->
            <div v-if="error" class="text-flamingo-800">{{ error }}</div> <!-- Display error message -->
            <SpinnerComponent v-if="isLoading" />
            <form v-else class="flex flex-col space-y-4" @submit.prevent="addParticipant" method="POST">
                <label class="block">
                    <select name="title"
                        class="mt-2 py-3 px-3 bg-white border shadow-sm border-ghost-600 placeholder-slate-400 focus:outline-none focus:border-athens-gray-500 focus:border-athens-gray-500 block w-full rounded-md sm:text-sm focus:ring-1"
                        v-model="participantData.title">
                        <option value="" disabled selected>--Select title--</option>
                        <option value="Mr" selected>Mr</option>
                        <option value="Mrs" selected>Mrs</option>
                        <option value="Ms" selected>Ms</option>
                        <option value="Miss" selected>Miss</option>
                        <option value="Dr" selected>Dr</option>
                        <option value="Prof" selected>Prof</option>
                        <option value="Prof" selected>Esq</option>
                    </select>
                </label>
                <label class="flex sm:flex-row flex-col sm:space-x-4 space-y-2">
                    <input type="text" name="firstname" v-model="participantData.firstname"
                        class="mt-2 py-3 px-3 bg-white border shadow-sm border-ghost-600 placeholder-slate-400 focus:outline-none focus:border-athens-gray-500 focus:border-athens-gray-500 block w-full rounded-md sm:text-sm focus:ring-1"
                        placeholder="Firstname" required />
                    <input type="text" name="lastname" v-model="participantData.lastname"
                        class="mt-2 py-3 px-3 bg-white border shadow-sm border-ghost-600 placeholder-slate-400 focus:outline-none focus:border-athens-gray-500 focus:border-athens-gray-500 block w-full rounded-md sm:text-sm focus:ring-1"
                        placeholder="Lastname" required />
                </label>
                <label class="flex sm:flex-row flex-col sm:space-x-4 space-y-2">
                    <input type="text" name="phone" v-model="participantData.phone"
                        class="mt-2 py-3 px-3 bg-white border shadow-sm border-ghost-600 placeholder-slate-400 focus:outline-none focus:border-athens-gray-500 focus:border-athens-gray-500 block w-full rounded-md sm:text-sm focus:ring-1"
                        placeholder="Phone" required />
                    <input type="email" name="email" v-model="participantData.email"
                        class="mt-2 py-3 px-3 bg-white border shadow-sm border-ghost-600 placeholder-slate-400 focus:outline-none focus:border-athens-gray-500 focus:border-athens-gray-500 block w-full rounded-md sm:text-sm focus:ring-1"
                        placeholder="Email" required />
                </label>
                <label class="flex sm:flex-row flex-col sm:space-x-4 space-y-2">
                    <input type="text" name="institution" v-model="participantData.institution"
                        class="mt-2 py-3 px-3 bg-white border shadow-sm border-ghost-600 placeholder-slate-400 focus:outline-none focus:border-athens-gray-500 focus:border-athens-gray-500 block w-full rounded-md sm:text-sm focus:ring-1"
                        placeholder="Institution" required />
                    <select name="country"
                        class="mt-2 px-3 py-3 bg-white border border-1 shadow-sm border-mid-gray-300 placeholder-slate-400 focus:outline-none focus:border-sky-500 focus:ring-sky-500 block w-full rounded-md sm:text-sm focus:ring-1"
                        v-model="participantData.country_id">
                        <option value="" disabled selected>--Select country--</option>
                        <option v-for="country in countries" :key="country.id" :value="country.id">
                            {{ country.country }}
                        </option>
                    </select>
                </label>
                <div class="flex sm:flex-row flex-col sm:space-x-4 space-y-2">
                    <button type="submit"
                        class="flex-1 px-4 py-3 text-white-50 rounded-md bg-bondi-blue text-stone-100 hover:bg-bondi-blue-600">
                        Register
                    </button>
                </div>
                <div class="flex sm:flex-row flex-col sm:space-x-4 justify-center items-center">
                    <p class="">
                        Already have an account? <router-link :to="{ name: 'Login' }"
                            class="cursor-poiter text-bondi-blue-500 cursor-pointer">Sign
                            in</router-link>
                    </p>
                </div>
            </form>
        </div>
    </div>
</template>

<script>
import { createItem, fetchData } from "@/services/apiService";
import SpinnerComponent from "@/components/Spinner.vue";

export default {
    name: 'RegisterView',
    components: {
        SpinnerComponent
    },
    data() {
        return {
            headerTitle: "Add participant",
            participantData: {
                title: "",
                firstname: "",
                lastname: "",
                institution: "",
                country: "",
                email: "",
                phone: "",
            },
            isLoading: false,
            countries: {},
            currentPage: 1,
            totalPages: "",
            pageSize: 500,
            searchPhrase: "",
            message: '',
            error: ''
        };
    },
    mounted() {
        this.getCountries();
    },
    methods: {
        async addParticipant() {
            this.isLoading = true;
            try {
                const response = await createItem("participants/", this.participantData);
                this.participants = response.data;
                this.isLoading = false;
                this.message = "Your regsitration was succesful, check your email for details"
            } catch (error) {
                console.error("Error fetching participants:", error);
                this.error = "Account already exists, please login or reset password"
                this.isLoading = false;
            }
        },
        async getCountries() {
            try {
                const response = await fetchData("countries", this.currentPage, this.pageSize, this.searchPhrase);
                this.countries = response.data;
                this.isLoading = false;
            } catch (error) {
                console.error("Error fetching countries:", error);
                this.error = error
                this.isLoading = false;
            }
        },
    },
}
</script>