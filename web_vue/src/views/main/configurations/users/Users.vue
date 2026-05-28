<template>
  <div class="flex flex-col space-y-4 flex-1">
    <HeaderView :headerTitle="'System Users'" />

    <div class="flex flex-col space-y-4">
      <!-- Toolbar -->
      <div class="flex sm:flex-row flex-col sm:justify-between sm:items-center items-start gap-3">
        <search-component @search="handleSearch"></search-component>
        <router-link v-if="permissions.includes('ADD_USER')"
          :to="{ name: 'AddUser' }"
          class="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl text-white text-sm font-semibold transition hover:opacity-90"
          style="background-color: rgb(254,80,103);">
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
          </svg>
          Add User
        </router-link>
      </div>

      <SpinnerComponent v-if="isLoading" />

      <div v-else class="bg-white rounded-2xl shadow-sm overflow-hidden">
        <!-- Table header -->
        <div class="hidden sm:grid grid-cols-12 gap-2 bg-gray-50 px-5 py-3 text-xs font-bold uppercase tracking-wider text-gray-500 border-b border-gray-100">
          <div class="col-span-1">#</div>
          <div class="col-span-3">Name</div>
          <div class="col-span-3">Email</div>
          <div class="col-span-2">Phone</div>
          <div class="col-span-2">Role</div>
          <div class="col-span-1 text-right">Actions</div>
        </div>

        <!-- Empty -->
        <div v-if="!users || users.length === 0" class="py-16 text-center">
          <p class="text-gray-400 text-sm italic">No users found.</p>
        </div>

        <!-- Rows -->
        <div v-for="(user, idx) in users" :key="user.id"
          class="flex sm:grid sm:grid-cols-12 gap-2 items-center px-5 py-3.5 border-b border-gray-50 hover:bg-gray-50 transition text-sm">
          <!-- # -->
          <div class="col-span-1 text-gray-400 text-xs hidden sm:block">
            {{ (currentPage - 1) * pageSize + idx + 1 }}
          </div>
          <!-- Name + avatar -->
          <div class="col-span-3 flex items-center gap-3">
            <div class="h-8 w-8 rounded-full flex items-center justify-center text-white text-xs font-bold flex-shrink-0"
              style="background-color: rgb(254,80,103);">
              {{ (user.firstname?.charAt(0) || '').toUpperCase() }}{{ (user.lastname?.charAt(0) || '').toUpperCase() }}
            </div>
            <div class="min-w-0">
              <p class="font-semibold text-gray-800 text-sm truncate">{{ user.firstname }} {{ user.lastname }}</p>
            </div>
          </div>
          <!-- Email -->
          <div class="col-span-3 text-gray-500 text-xs truncate">{{ user.email || '—' }}</div>
          <!-- Phone -->
          <div class="col-span-2 text-gray-600 text-xs">{{ user.phone || '—' }}</div>
          <!-- Role -->
          <div class="col-span-2 text-xs">
            <span v-if="user.role"
              class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold"
              style="background-color: rgba(254,80,103,0.1); color: rgb(254,80,103);">
              {{ user.role }}
            </span>
            <span v-else class="text-gray-300">—</span>
          </div>
          <!-- Actions -->
          <div class="col-span-1 flex justify-end gap-1.5">
            <router-link v-if="permissions.includes('VIEW_USER')"
              :to="{ name: 'User', params: { id: user.id } }"
              class="p-1.5 rounded-lg text-gray-400 hover:bg-gray-100 hover:text-gray-700 transition"
              title="View user">
              <EyeIcon class="w-4 h-4" />
            </router-link>
            <router-link v-if="permissions.includes('UPDATE_USER')"
              :to="{ name: 'EditUser', params: { id: user.id } }"
              class="p-1.5 rounded-lg text-gray-400 hover:bg-blue-50 hover:text-blue-600 transition"
              title="Edit user">
              <PencilSquareIcon class="w-4 h-4" />
            </router-link>
            <button v-if="permissions.includes('DELETE_USER')"
              @click="showDeleteConfirmation(user.id)"
              class="p-1.5 rounded-lg text-gray-400 hover:bg-red-50 hover:text-red-500 transition"
              title="Delete user">
              <TrashIcon class="w-4 h-4" />
            </button>
          </div>
        </div>

        <div class="px-5 py-3 border-t border-gray-50">
          <pagination-component :currentPage="currentPage" :totalPages="totalPages"
            @page-change="handlePageChange" />
        </div>
      </div>
    </div>

    <delete-confirmation-modal :show="showDeleteModal"
      @confirmed="deleteUser(deleteUserId)"
      @canceled="cancelDelete" />
  </div>
</template>

<script>
import HeaderView from '@/includes/Header.vue'
import { EyeIcon, PencilSquareIcon, TrashIcon } from '@heroicons/vue/24/solid'
import PaginationComponent from '@/components/PaginationComponent.vue'
import SearchComponent from '@/components/SearchComponent.vue'
import { fetchData, deleteItem } from '@/services/apiService'
import SpinnerComponent from '@/components/Spinner.vue'
import DeleteConfirmationModal from '@/components/DeleteConfirmationModal.vue'
import { useAuthStore } from '@/store/authStore'

export default {
  name: 'UsersView',
  components: {
    EyeIcon, PencilSquareIcon, TrashIcon,
    PaginationComponent, SearchComponent, HeaderView, SpinnerComponent, DeleteConfirmationModal,
  },
  data() {
    return {
      users: [],
      isLoading: true,
      showDeleteModal: false,
      deleteUserId: null,
      currentPage: 1,
      totalPages: 1,
      pageSize: 20,
      searchPhrase: '',
    }
  },
  setup() {
    const authStore = useAuthStore()
    const raw = authStore.permissions || []
    const permissions = raw.map(p => typeof p === 'string' ? p : p.permission_code)
    return { permissions }
  },
  mounted() {
    this.getUsers()
  },
  methods: {
    async getUsers() {
      this.isLoading = true
      try {
        const response = await fetchData('users', (this.currentPage - 1) * this.pageSize, this.pageSize, this.searchPhrase)
        this.users = response.data || []
        this.totalPages = response.pages || 1
      } catch (error) {
        console.error('Error fetching users:', error)
      } finally {
        this.isLoading = false
      }
    },
    handleSearch(query) {
      this.searchPhrase = query
      this.currentPage = 1
      this.getUsers()
    },
    handlePageChange(newPage) {
      this.currentPage = newPage
      this.getUsers()
    },
    async deleteUser(id) {
      this.isLoading = true
      try {
        await deleteItem('users', id)
        this.users = this.users.filter(u => u.id !== id)
        this.showDeleteModal = false
      } catch (error) {
        console.error('Error deleting user:', error)
        this.showDeleteModal = false
      } finally {
        this.isLoading = false
      }
    },
    showDeleteConfirmation(id) {
      this.deleteUserId = id
      this.showDeleteModal = true
    },
    cancelDelete() {
      this.showDeleteModal = false
    },
  },
}
</script>
