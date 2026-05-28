<!-- src/components/Dropdown.vue -->
<template>
    <div class="relative inline-block text-left">
        <div @click="isOpen = !isOpen" class="flex flex-row items-center space-x-2 cursor-pointer">
            <UserCircleIcon class="w-8 h-8 text-bondi-blue-700"></UserCircleIcon>
            <span class=" text-sm text-catskill-white-500"> {{ loginUser.firstname }}
                {{ loginUser.lastname }}</span>
        </div>

        <div v-if="isOpen" class="origin-top-right absolute right-0 mt-2 w-32 rounded-xl shadow-lg bg-bondi-blue-50">
            <div class="py-2 space-y-2" role="menu" aria-orientation="vertical" aria-labelledby="options-menu">
                <a @click="profile" class="block px-4 cursor-pointer text-sm text-gray-700 hover:bg-gray-100"
                    role="menuitem">
                    My profile
                </a>
                <a @click="logout" class="block px-4 cursor-pointer text-sm text-gray-700 hover:bg-gray-100"
                    role="menuitem">
                    Logout
                </a>
            </div>
        </div>
    </div>
</template>

<script>
import router from "@/router";
import { UserCircleIcon } from '@heroicons/vue/24/solid'
import { useAuthStore } from "@/store/authStore";

export default {
    name: "ProfileComponent",
    components: {
        UserCircleIcon
    },
    props: {
        label: String,
    },
    data() {
        return {
            isOpen: false,
        };
    },
    setup() {
        const authStore = useAuthStore()
        const loginUser = authStore.loginUser
        return { loginUser }
    },
    methods: {
        async profile() { router.push("/my-profile/" + this.loginUser.id); },

        async logout() {
            localStorage.removeItem("authToken");
            router.push("/");
        }


    }
};
</script>