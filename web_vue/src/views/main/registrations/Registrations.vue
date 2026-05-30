<template>
  <div class="flex flex-col space-y-4 flex-1">
    <HeaderView :headerTitle="headerTitle"></HeaderView>

    <div class="flex flex-col space-y-4">
      <!-- Search + event filter -->
      <div class="flex sm:flex-row flex-col sm:justify-between sm:items-center items-start gap-3 flex-wrap">
        <search-component @search="handleSearch"></search-component>
        <div class="flex items-center gap-2 flex-wrap">
          <select v-model="selectedEventId" @change="handleFilterChange"
            class="border border-gray-200 rounded-lg px-3 py-2 text-sm text-gray-700 focus:outline-none focus:border-pink-400 bg-white min-w-[180px]">
            <option value="">All Events</option>
            <option v-for="event in events" :key="event.id" :value="event.id">{{ event.event }}</option>
          </select>
          <select v-model="paidFilter" @change="handleFilterChange"
            class="border border-gray-200 rounded-lg px-3 py-2 text-sm text-gray-700 focus:outline-none focus:border-pink-400 bg-white">
            <option value="all">All Payments</option>
            <option value="true">Paid</option>
            <option value="false">Unpaid</option>
          </select>
        </div>
      </div>

      <!-- Spinner -->
      <SpinnerComponent v-if="isLoading" />

      <div v-else class="bg-white rounded-2xl shadow-sm overflow-hidden">
        <!-- Table header -->
        <div class="hidden sm:grid grid-cols-12 gap-2 bg-gray-50 px-5 py-3 text-xs font-bold uppercase tracking-wider text-gray-500 border-b border-gray-100">
          <div class="col-span-1">#</div>
          <div class="col-span-2">Participant</div>
          <div class="col-span-2">Email</div>
          <div class="col-span-2">Event</div>
          <div class="col-span-2">Category</div>
          <div class="col-span-1">Date</div>
          <div class="col-span-1">Payment</div>
          <div class="col-span-1 text-right"></div>
        </div>

        <!-- Empty state -->
        <div v-if="registrations.length === 0" class="flex flex-col items-center justify-center py-16 text-center px-6">
          <div class="h-14 w-14 rounded-full flex items-center justify-center mb-4"
            style="background-color: rgba(254,80,103,0.1);">
            <svg class="w-7 h-7" style="color: rgb(254,80,103);" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
          </div>
          <p class="text-gray-400 text-sm italic">No registrations found.</p>
        </div>

        <!-- Rows -->
        <div v-for="(reg, idx) in registrations" :key="reg.id || reg.registration_id"
          class="flex sm:grid sm:grid-cols-12 gap-2 items-center px-5 py-3.5 border-b border-gray-50 hover:bg-gray-50 transition text-sm">
          <!-- # -->
          <div class="col-span-1 text-gray-400 text-xs font-medium hidden sm:block">
            {{ (currentPage - 1) * pageSize + idx + 1 }}
          </div>
          <!-- Participant — click to open user profile -->
          <div class="col-span-2">
            <router-link
              v-if="reg.user_id"
              :to="{ name: 'User', params: { id: reg.user_id } }"
              class="font-semibold hover:underline transition"
              style="color: rgb(254,80,103);">
              {{ [reg.title, reg.firstname, reg.lastname].filter(Boolean).join(' ') || '—' }}
            </router-link>
            <span v-else class="font-semibold text-gray-800">
              {{ [reg.title, reg.firstname, reg.lastname].filter(Boolean).join(' ') || '—' }}
            </span>
          </div>
          <!-- Email -->
          <div class="col-span-2 text-gray-500 truncate">{{ reg.email || '—' }}</div>
          <!-- Event -->
          <div class="col-span-2 text-gray-700 text-xs">{{ reg.event || '—' }}</div>
          <!-- Category -->
          <div class="col-span-2 text-gray-600 text-xs leading-tight">
            {{ reg.participation_role ? formatRole(reg.participation_role) : '—' }}
          </div>
          <!-- Date -->
          <div class="col-span-1 text-gray-400 text-xs whitespace-nowrap">
            {{ formatDate(reg.registered_at || reg.created_at) }}
          </div>
          <!-- Payment badge -->
          <div class="col-span-1">
            <span v-if="reg.paid"
              class="inline-flex items-center px-2 py-1 rounded-full text-xs font-semibold bg-green-100 text-green-700">
              Paid
            </span>
            <span v-else-if="reg.payment_proof"
              class="inline-flex items-center px-2 py-1 rounded-full text-xs font-semibold bg-blue-100 text-blue-700">
              Proof Sent
            </span>
            <span v-else
              class="inline-flex items-center px-2 py-1 rounded-full text-xs font-semibold bg-yellow-100 text-yellow-700">
              Pending
            </span>
          </div>
          <!-- Actions — kebab popover -->
          <div class="col-span-1 flex justify-end" style="position: relative;">
            <button
              @click.stop="toggleMenu(reg.id || reg.registration_id)"
              class="w-7 h-7 rounded-lg flex items-center justify-center text-gray-400 hover:text-gray-700 hover:bg-gray-100 transition">
              <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                <circle cx="12" cy="5"  r="1.5"/><circle cx="12" cy="12" r="1.5"/><circle cx="12" cy="19" r="1.5"/>
              </svg>
            </button>
            <!-- Dropdown -->
            <transition name="pop">
              <div v-if="openMenuId === (reg.id || reg.registration_id)"
                class="absolute right-0 top-8 z-30 w-44 bg-white rounded-xl shadow-lg border border-gray-100 py-1 text-sm"
                @click.stop>
                <!-- View proof -->
                <button v-if="reg.payment_proof"
                  @click="viewProof(reg); closeMenu()"
                  class="w-full flex items-center gap-2.5 px-4 py-2 text-gray-700 hover:bg-gray-50 transition">
                  <svg class="w-4 h-4 text-gray-400 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
                  </svg>
                  View File
                </button>
                <div v-if="reg.payment_proof" class="border-t border-gray-50 mx-3"></div>
                <!-- Edit -->
                <button
                  @click="openEditModal(reg); closeMenu()"
                  class="w-full flex items-center gap-2.5 px-4 py-2 text-gray-700 hover:bg-gray-50 transition">
                  <svg class="w-4 h-4 text-gray-400 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
                  </svg>
                  Edit
                </button>
                <div class="border-t border-gray-50 mx-3"></div>
                <!-- Verify -->
                <button v-if="!reg.paid"
                  @click="verifyPayment(reg); closeMenu()"
                  :disabled="verifyingId === (reg.id || reg.registration_id)"
                  class="w-full flex items-center gap-2.5 px-4 py-2 font-semibold hover:bg-green-50 transition disabled:opacity-50"
                  style="color: rgb(22,163,74);">
                  <svg class="w-4 h-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
                  </svg>
                  {{ verifyingId === (reg.id || reg.registration_id) ? 'Verifying…' : 'Verify Payment' }}
                </button>
                <!-- Unverify -->
                <button v-else
                  @click="unverifyPayment(reg); closeMenu()"
                  :disabled="verifyingId === (reg.id || reg.registration_id)"
                  class="w-full flex items-center gap-2.5 px-4 py-2 font-semibold hover:bg-red-50 transition disabled:opacity-50"
                  style="color: rgb(254,80,103);">
                  <svg class="w-4 h-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                  </svg>
                  {{ verifyingId === (reg.id || reg.registration_id) ? 'Processing…' : 'Unverify' }}
                </button>
                <!-- Delete -->
                <div class="border-t border-gray-100 mx-3 my-1"></div>
                <button
                  @click="confirmDelete(reg); closeMenu()"
                  class="w-full flex items-center gap-2.5 px-4 py-2 font-semibold text-red-600 hover:bg-red-50 transition">
                  <svg class="w-4 h-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                  </svg>
                  Delete Registration
                </button>
              </div>
            </transition>
          </div>
        </div>
      </div>

      <!-- Toast notification -->
      <transition name="fade">
        <div v-if="toast.show"
          class="fixed bottom-6 right-6 z-50 px-5 py-3 rounded-xl text-white text-sm font-semibold shadow-lg"
          :style="toast.type === 'success' ? 'background-color: rgb(34,197,94);' : 'background-color: rgb(239,68,68);'">
          {{ toast.message }}
        </div>
      </transition>

      <!-- Pagination -->
      <pagination-component :currentPage="currentPage" :totalPages="totalPages"
        @page-change="handlePageChange">
      </pagination-component>
    </div>

    <!-- Edit Registration Modal -->
    <div v-if="editModal.show"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4"
      @click.self="closeEditModal">
      <div class="bg-white rounded-2xl shadow-xl w-full max-w-2xl flex flex-col max-h-[92vh] overflow-hidden">
        <!-- Header -->
        <div class="flex items-center justify-between px-6 py-4 border-b border-gray-100"
          style="background-color: rgba(254,80,103,0.04);">
          <div>
            <p class="font-bold text-gray-800">Edit Registration</p>
            <p class="text-xs text-gray-400 mt-0.5">{{ editModal.participantName }}</p>
          </div>
          <button @click="closeEditModal" class="text-gray-400 hover:text-gray-600 transition">
            <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>

        <!-- Form body -->
        <div class="p-6 overflow-y-auto flex-1 space-y-4">
          <!-- Error -->
          <div v-if="editModal.error"
            class="p-3 rounded-xl bg-red-50 border border-red-200 text-red-700 text-sm">
            {{ editModal.error }}
          </div>

          <div class="grid sm:grid-cols-2 gap-4">
            <!-- Title -->
            <div>
              <label class="edit-label">Title</label>
              <select v-model="editForm.title" class="edit-input">
                <option value="">Select title</option>
                <option value="Mr.">Mr.</option>
                <option value="Mrs.">Mrs.</option>
                <option value="Ms.">Ms.</option>
                <option value="Dr.">Dr.</option>
                <option value="Prof.">Prof.</option>
                <option value="Sr.">Sr.</option>
              </select>
            </div>
            <!-- Phone -->
            <div>
              <label class="edit-label">Phone</label>
              <input v-model="editForm.phone" type="tel" class="edit-input" placeholder="+255700000000" />
            </div>
            <!-- First Name -->
            <div>
              <label class="edit-label">First Name <span class="text-red-500">*</span></label>
              <input v-model="editForm.firstname" type="text" class="edit-input" placeholder="First name" />
            </div>
            <!-- Last Name -->
            <div>
              <label class="edit-label">Last Name <span class="text-red-500">*</span></label>
              <input v-model="editForm.lastname" type="text" class="edit-input" placeholder="Last name" />
            </div>
            <!-- Email (readonly) -->
            <div class="sm:col-span-2">
              <label class="edit-label">Email <span class="text-xs text-gray-400">(cannot change)</span></label>
              <input :value="editModal.email" type="email" class="edit-input bg-gray-50 text-gray-400 cursor-not-allowed" readonly />
            </div>
            <!-- Country -->
            <div>
              <label class="edit-label">Country</label>
              <select v-model="editForm.country_id" class="edit-input">
                <option value="">Select country</option>
                <option v-for="c in editCountries" :key="c.id" :value="c.id">{{ c.country }}</option>
              </select>
            </div>
            <!-- Address -->
            <div class="sm:col-span-2">
              <label class="edit-label">Address</label>
              <textarea v-model="editForm.address" rows="2" class="edit-input" placeholder="Street / PO Box, City, Region"></textarea>
            </div>
            <!-- Designation -->
            <div class="sm:col-span-2">
              <label class="edit-label">Designation</label>
              <select v-model="editForm.designation" class="edit-input">
                <option value="">Select designation</option>
                <option value="Chief Nursing Officer">Chief Nursing Officer</option>
                <option value="Clinical Supervisor">Clinical Supervisor</option>
                <option value="Communications Manager">Communications Manager</option>
                <option value="Director Nursing Services">Director Nursing Services</option>
                <option value="Educator">Educator</option>
                <option value="Midwifery Specialist">Midwifery Specialist</option>
                <option value="Nursing Midwifery Specialist">Nursing Midwifery Specialist</option>
                <option value="Nursing Specialist">Nursing Specialist</option>
                <option value="Nursing Superintendent">Nursing Superintendent</option>
                <option value="Principal Nursing Officer">Principal Nursing Officer</option>
                <option value="Project Manager">Project Manager</option>
                <option value="Public Health Specialist">Public Health Specialist</option>
                <option value="Registered Nurse">Registered Nurse</option>
                <option value="Researcher">Researcher</option>
                <option value="Student">Student</option>
                <option value="Other">Other (specify below)</option>
              </select>
            </div>
            <div v-if="editForm.designation === 'Other'" class="sm:col-span-2">
              <label class="edit-label">Specify Designation <span class="text-red-500">*</span></label>
              <input v-model="editForm.designation_other" type="text" class="edit-input" placeholder="Your designation" />
            </div>
            <!-- Organisation -->
            <div class="sm:col-span-2">
              <label class="edit-label">Organisation / Institution</label>
              <input v-model="editForm.organisation" type="text" class="edit-input" placeholder="e.g. Ministry of Health" />
            </div>
          </div>

          <!-- Participation Category -->
          <div>
            <label class="edit-label">Participation Category</label>
            <div class="grid grid-cols-1 gap-2 mt-2">
              <label v-for="opt in participationOptions" :key="opt.value"
                class="flex items-start gap-3 p-3 rounded-xl border-2 cursor-pointer transition"
                :style="editForm.participation_role === opt.value
                  ? 'border-color: rgb(254,80,103); background-color: rgba(254,80,103,0.05);'
                  : 'border-color: #e5e7eb; background-color: #fff;'">
                <input type="radio" :value="opt.value" v-model="editForm.participation_role"
                  class="mt-0.5 accent-pink-500 flex-shrink-0" />
                <div>
                  <span class="text-sm font-semibold text-gray-800">{{ opt.label }}</span>
                  <p v-if="opt.fee" class="text-xs text-gray-500 mt-0.5">{{ opt.fee }}</p>
                </div>
              </label>
            </div>
          </div>

          <!-- Passport Photo (optional) -->
          <div>
            <label class="edit-label">Passport Photo <span class="text-xs text-gray-400">(optional)</span></label>
            <div class="flex items-center gap-4 mt-2">
              <div v-if="editForm.photoPreview"
                class="h-16 w-16 rounded-full overflow-hidden border-2 flex-shrink-0"
                style="border-color: rgb(254,80,103);">
                <img :src="editForm.photoPreview" alt="Photo preview" class="h-full w-full object-cover" />
              </div>
              <label class="cursor-pointer">
                <div class="flex items-center gap-2 px-4 py-2 rounded-xl border-2 border-dashed text-sm font-semibold transition"
                  style="border-color: rgba(254,80,103,0.4); color: rgb(254,80,103);">
                  <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                  {{ editForm.photo ? 'Change Photo' : 'Upload Photo' }}
                </div>
                <input type="file" accept="image/*" class="hidden" @change="onEditPhotoChange" />
              </label>
              <span v-if="editForm.photo" class="text-xs text-gray-400">{{ editForm.photo.name }}</span>
            </div>
          </div>
        </div>

        <!-- Footer -->
        <div class="flex items-center justify-end gap-3 px-6 py-4 border-t border-gray-100">
          <button @click="closeEditModal"
            class="px-5 py-2 rounded-xl text-sm font-semibold border border-gray-200 text-gray-600 hover:bg-gray-50 transition">
            Cancel
          </button>
          <button @click="saveEditRegistration"
            :disabled="editModal.saving"
            class="px-5 py-2 rounded-xl text-sm font-semibold text-white hover:opacity-90 disabled:opacity-50 transition"
            style="background-color: rgb(254,80,103);">
            {{ editModal.saving ? 'Saving…' : 'Save Changes' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Proof of Payment Modal -->
    <div v-if="proofModal.show"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4"
      @click.self="closeProof">
      <div class="bg-white rounded-2xl shadow-xl max-w-2xl w-full flex flex-col max-h-[90vh] overflow-hidden">
        <!-- Modal header -->
        <div class="flex items-center justify-between px-6 py-4 border-b border-gray-100"
          style="background-color: rgba(254,80,103,0.04);">
          <div>
            <p class="font-bold text-gray-800">Payment Proof</p>
            <p class="text-xs text-gray-400 mt-0.5">{{ proofModal.participantName }}</p>
          </div>
          <button @click="closeProof" class="text-gray-400 hover:text-gray-600 transition">
            <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>
        <!-- Proof content -->
        <div class="p-6 overflow-y-auto flex-1">
          <!-- Image -->
          <div v-if="isImageProof(proofModal.proofUrl)" class="rounded-xl overflow-hidden border border-gray-100">
            <img :src="proofModal.proofUrl" alt="Payment proof" class="w-full max-h-96 object-contain bg-gray-50" />
          </div>
          <!-- PDF — embedded inline -->
          <div v-else>
            <iframe
              :src="proofModal.proofUrl"
              class="w-full rounded-xl border border-gray-200"
              style="height: 480px;"
              title="Payment Proof PDF">
            </iframe>
            <a :href="proofModal.proofUrl" target="_blank"
              class="inline-flex items-center gap-1.5 mt-3 text-xs font-semibold hover:underline"
              style="color: rgb(254,80,103);">
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
              </svg>
              Open in new tab
            </a>
          </div>
          <!-- Actions -->
          <div class="flex justify-end gap-3 mt-5 pt-4 border-t border-gray-100">
            <button @click="closeProof"
              class="px-5 py-2 rounded-xl text-sm font-semibold border border-gray-200 text-gray-600 hover:bg-gray-50 transition">
              Close
            </button>
            <button v-if="!proofModal.reg.paid"
              @click="verifyFromModal"
              :disabled="verifyingId === proofModal.regId"
              class="px-5 py-2 rounded-xl text-sm font-semibold text-white hover:opacity-90 disabled:opacity-50 transition"
              style="background-color: rgb(254,80,103);">
              {{ verifyingId === proofModal.regId ? 'Verifying…' : 'Verify Payment' }}
            </button>
            <button v-else
              @click="unverifyFromModal"
              :disabled="verifyingId === proofModal.regId"
              class="px-5 py-2 rounded-xl text-sm font-semibold border-2 hover:bg-red-50 disabled:opacity-50 transition"
              style="border-color: rgb(254,80,103); color: rgb(254,80,103);">
              {{ verifyingId === proofModal.regId ? 'Processing…' : 'Un-verify' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- ── Delete Confirmation Modal ─────────────────────────────────────────── -->
    <div v-if="deleteModal.show"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4"
      @click.self="deleteModal.show = false">
      <div class="bg-white rounded-2xl shadow-xl w-full max-w-sm p-7 text-center">
        <div class="h-14 w-14 rounded-full bg-red-100 flex items-center justify-center mx-auto mb-4">
          <svg class="w-7 h-7 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
          </svg>
        </div>
        <h3 class="text-lg font-bold text-gray-800 mb-1">Delete Registration?</h3>
        <p class="text-sm text-gray-500 mb-1">
          <strong>{{ [deleteModal.reg?.title, deleteModal.reg?.firstname, deleteModal.reg?.lastname].filter(Boolean).join(' ') }}</strong>
        </p>
        <p class="text-sm text-gray-400 mb-6">This will remove the registration. The user account will remain. They can register again afterwards.</p>
        <div class="flex gap-3">
          <button @click="deleteModal.show = false" :disabled="deleteModal.deleting"
            class="flex-1 py-2.5 rounded-xl font-semibold text-sm text-gray-600 bg-gray-100 hover:bg-gray-200 transition disabled:opacity-50">
            Cancel
          </button>
          <button @click="deleteRegistration" :disabled="deleteModal.deleting"
            class="flex-1 py-2.5 rounded-xl font-semibold text-sm text-white bg-red-600 hover:bg-red-700 transition disabled:opacity-50">
            {{ deleteModal.deleting ? 'Deleting…' : 'Delete' }}
          </button>
        </div>
      </div>
    </div>

  </div>
</template>

<script>
import axios from 'axios'
import HeaderView from '@/includes/Header.vue'
import PaginationComponent from '@/components/PaginationComponent.vue'
import SearchComponent from '@/components/SearchComponent.vue'
import SpinnerComponent from '@/components/Spinner.vue'
import { fetchData, fetchDataWithParams, updateItem } from '@/services/apiService'
import { useAuthStore } from '@/store/authStore'

const API_URL = import.meta.env.VITE_API_URL

export default {
  name: 'RegistrationsView',
  components: {
    PaginationComponent, SearchComponent, HeaderView, SpinnerComponent,
  },
  data() {
    return {
      headerTitle: 'Registrations',
      registrations: [],
      events: [],
      isLoading: true,
      verifyingId: null,
      currentPage: 1,
      totalPages: 1,
      pageSize: 20,
      searchPhrase: '',
      selectedEventId: '',
      paidFilter: 'all',
      openMenuId: null,
      deleteModal: { show: false, reg: null, deleting: false },
      toast: { show: false, message: '', type: 'success' },
      proofModal: {
        show: false,
        proofUrl: '',
        participantName: '',
        regId: null,
        reg: {},
      },
      editModal: {
        show: false,
        regId: null,
        participantName: '',
        email: '',
        error: '',
        saving: false,
      },
      editForm: {
        title: '',
        firstname: '',
        lastname: '',
        phone: '',
        country_id: '',
        address: '',
        designation: '',
        designation_other: '',
        organisation: '',
        participation_role: '',
        photo: null,
        photoPreview: '',
      },
      editCountries: [],
      participationOptions: [
        { value: 'member_state', label: 'ECSACONM Member (no arrears)', fee: 'Early Bird: USD 200 | Late Bird: USD 250' },
        { value: 'participant', label: 'Non-ECSACONM Member from the Region', fee: 'Early Bird: USD 300 | Late Bird: USD 400' },
        { value: 'other_africa', label: 'Non-ECSACONM Member from Outside the Region', fee: 'Early Bird: USD 400 | Late Bird: USD 600' },
        { value: 'student', label: 'Student', fee: 'Contact the secretariat for student rates.' },
        { value: 'exhibitor', label: 'Sponsor / Exhibitor', fee: 'Contact the secretariat for sponsorship packages.' },
        { value: 'secretariat', label: 'Secretariat / Staff', fee: 'Internal registration — no registration fee.' },
      ],
    }
  },
  setup() {
    const authStore = useAuthStore()
    const raw = authStore.permissions || []
    const permissions = raw.map(p => typeof p === "string" ? p : p.permission_code)
    return { permissions, authStore }
  },
  mounted() {
    this.loadEvents()
    this.loadRegistrations()
    document.addEventListener('click', this.closeMenu)
  },
  beforeUnmount() {
    document.removeEventListener('click', this.closeMenu)
  },
  methods: {
    async loadEvents() {
      try {
        const response = await fetchData('events', 0, 200, '')
        this.events = response.data || []
      } catch (error) {
        console.error('Error fetching events:', error)
      }
    },
    async loadRegistrations() {
      this.isLoading = true
      try {
        const params = {
          skip: (this.currentPage - 1) * this.pageSize,
          limit: this.pageSize,
          search: this.searchPhrase || '',
          paid: this.paidFilter,
        }
        if (this.selectedEventId) params.event_id = this.selectedEventId
        const response = await fetchDataWithParams('registrations', params)
        this.registrations = response.data || response || []
        this.totalPages = response.pages || 1
      } catch (error) {
        console.error('Error fetching registrations:', error)
        this.registrations = []
      } finally {
        this.isLoading = false
      }
    },
    async verifyPayment(reg) {
      const regId = reg.id || reg.registration_id
      this.verifyingId = regId
      try {
        const token = this.authStore.accessToken
        const api = axios.create({ baseURL: API_URL })
        if (token) api.defaults.headers.common['Authorization'] = `Bearer ${token}`
        await api.put(`/events/verify_payment/${regId}`, {})
        const index = this.registrations.findIndex(r => (r.id || r.registration_id) === regId)
        if (index !== -1) this.registrations[index].paid = true
        if (this.proofModal.regId === regId) this.proofModal.reg = { ...this.proofModal.reg, paid: true }
        this.showToast('Payment verified successfully!', 'success')
      } catch (error) {
        this.showToast(error.response?.data?.detail || 'Verification failed.', 'error')
      } finally {
        this.verifyingId = null
      }
    },
    async unverifyPayment(reg) {
      const regId = reg.id || reg.registration_id
      this.verifyingId = regId
      try {
        const token = this.authStore.accessToken
        const api = axios.create({ baseURL: API_URL })
        if (token) api.defaults.headers.common['Authorization'] = `Bearer ${token}`
        await api.put(`/events/unverify_payment/${regId}`, {})
        const index = this.registrations.findIndex(r => (r.id || r.registration_id) === regId)
        if (index !== -1) this.registrations[index].paid = false
        if (this.proofModal.regId === regId) this.proofModal.reg = { ...this.proofModal.reg, paid: false }
        this.showToast('Payment un-verified.', 'success')
      } catch (error) {
        this.showToast(error.response?.data?.detail || 'Failed to un-verify.', 'error')
      } finally {
        this.verifyingId = null
      }
    },
    viewProof(reg) {
      const regId = reg.id || reg.registration_id
      const name = [reg.title, reg.firstname, reg.lastname].filter(Boolean).join(' ')
      const proof = reg.payment_proof || ''
      const proofUrl = proof.startsWith('http') ? proof : `${API_URL}/${proof}`
      this.proofModal = {
        show: true,
        proofUrl,
        participantName: name,
        regId,
        reg,
      }
    },
    closeProof() {
      this.proofModal.show = false
    },
    verifyFromModal() {
      this.verifyPayment(this.proofModal.reg)
    },
    unverifyFromModal() {
      this.unverifyPayment(this.proofModal.reg)
    },
    isImageProof(url) {
      if (!url) return false
      return /\.(jpg|jpeg|png|gif|webp)$/i.test(url)
    },
    showToast(message, type = 'success') {
      this.toast = { show: true, message, type }
      setTimeout(() => { this.toast.show = false }, 3500)
    },
    handleSearch(query) {
      this.searchPhrase = query
      this.currentPage = 1
      this.loadRegistrations()
    },
    handlePageChange(newPage) {
      this.currentPage = newPage
      this.loadRegistrations()
    },
    handleFilterChange() {
      this.currentPage = 1
      this.loadRegistrations()
    },
    formatDate(dateString) {
      if (!dateString) return '—'
      return new Date(dateString).toLocaleDateString('en-GB', {
        day: '2-digit', month: 'short', year: 'numeric',
      })
    },
    confirmDelete(reg) {
      this.deleteModal = { show: true, reg, deleting: false }
    },
    async deleteRegistration() {
      const reg = this.deleteModal.reg
      const regId = reg.id || reg.registration_id
      this.deleteModal.deleting = true
      try {
        const { default: axios } = await import('axios')
        const api = axios.create({ baseURL: import.meta.env.VITE_API_URL })
        const { useAuthStore } = await import('@/store/authStore')
        const token = useAuthStore().accessToken
        if (token) api.defaults.headers.common['Authorization'] = `Bearer ${token}`
        await api.delete(`/events/deregister_participant/${regId}`)
        this.deleteModal = { show: false, reg: null, deleting: false }
        this.showToast('Registration deleted successfully.', 'success')
        await this.fetchRegistrations()
      } catch (e) {
        this.deleteModal.deleting = false
        this.showToast(e.response?.data?.detail || 'Failed to delete registration.', 'error')
      }
    },
    toggleMenu(id) {
      this.openMenuId = this.openMenuId === id ? null : id
    },
    closeMenu() {
      this.openMenuId = null
    },
    formatRole(role) {
      const map = {
        member_state: 'Member State',
        participant: 'Participant',
        other_africa: 'Other Africa',
        world: 'International',
        student: 'Student',
        exhibitor: 'Exhibitor/Sponsor',
        secretariat: 'Secretariat',
        delegate: 'Delegate',
        presenter: 'Presenter',
        speaker: 'Speaker',
        sponsor: 'Sponsor',
        moderator: 'Moderator',
        moh: 'Ministry of Health',
        member: 'Member',
        non_member_member_state: 'Non-Member (Member State)',
        non_member_other: 'Non-Member (Other)',
      }
      return map[role] || role
    },
    async loadEditCountries() {
      if (this.editCountries.length > 0) return
      try {
        const api = axios.create({ baseURL: API_URL })
        const token = this.authStore.accessToken
        if (token) api.defaults.headers.common['Authorization'] = `Bearer ${token}`
        const res = await api.get('/countries/?skip=0&limit=500')
        this.editCountries = res.data?.data || res.data || []
      } catch (e) {
        console.error('Error loading countries:', e)
      }
    },
    openEditModal(reg) {
      const name = [reg.title, reg.firstname, reg.lastname].filter(Boolean).join(' ')
      this.editModal = {
        show: true,
        regId: reg.id || reg.registration_id,
        participantName: name,
        email: reg.email || '',
        error: '',
        saving: false,
      }
      this.editForm = {
        title: reg.title || '',
        firstname: reg.firstname || '',
        lastname: reg.lastname || '',
        phone: reg.phone || '',
        country_id: reg.country_id || '',
        address: reg.address || '',
        designation: reg.designation || '',
        designation_other: '',
        organisation: reg.organisation || '',
        participation_role: reg.participation_role
          ? reg.participation_role.toLowerCase().replace(/\s+/g, '_')
          : '',
        photo: null,
        photoPreview: '',
      }
      this.loadEditCountries()
    },
    closeEditModal() {
      this.editModal.show = false
    },
    onEditPhotoChange(e) {
      const file = e.target.files && e.target.files[0]
      if (!file) return
      this.editForm.photo = file
      const reader = new FileReader()
      reader.onload = (evt) => { this.editForm.photoPreview = evt.target.result }
      reader.readAsDataURL(file)
    },
    async saveEditRegistration() {
      this.editModal.error = ''
      if (!this.editForm.firstname.trim()) {
        this.editModal.error = 'First name is required.'
        return
      }
      if (!this.editForm.lastname.trim()) {
        this.editModal.error = 'Last name is required.'
        return
      }
      this.editModal.saving = true
      try {
        const resolvedDesignation = this.editForm.designation === 'Other'
          ? this.editForm.designation_other
          : this.editForm.designation

        const payload = {
          title: this.editForm.title || null,
          firstname: this.editForm.firstname,
          lastname: this.editForm.lastname,
          phone: this.editForm.phone || null,
          country_id: this.editForm.country_id ? parseInt(this.editForm.country_id) : null,
          address: this.editForm.address || null,
          designation: resolvedDesignation || null,
          organisation: this.editForm.organisation || null,
          participation_role: this.editForm.participation_role || null,
        }

        await updateItem('registrations', this.editModal.regId, payload)

        // Upload photo if provided
        if (this.editForm.photo) {
          try {
            const api = axios.create({ baseURL: API_URL })
            const token = this.authStore.accessToken
            if (token) api.defaults.headers.common['Authorization'] = `Bearer ${token}`
            const photoForm = new FormData()
            photoForm.append('file', this.editForm.photo)
            // Get user_id from the registration row
            const reg = this.registrations.find(r => (r.id || r.registration_id) === this.editModal.regId)
            if (reg && reg.user_id) {
              await api.post(`/users/${reg.user_id}/photo`, photoForm, {
                headers: { 'Content-Type': 'multipart/form-data' },
              })
            }
          } catch (photoErr) {
            console.warn('Photo upload failed (non-critical):', photoErr)
          }
        }

        this.showToast('Registration updated successfully!', 'success')
        this.closeEditModal()
        await this.loadRegistrations()
      } catch (e) {
        this.editModal.error = e.response?.data?.detail
          || (Array.isArray(e.response?.data) ? e.response.data.map(x => x.msg).join(', ') : null)
          || 'Failed to save changes. Please try again.'
      } finally {
        this.editModal.saving = false
      }
    },
  },
}
</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

.pop-enter-active { transition: opacity 0.12s ease, transform 0.12s ease; }
.pop-leave-active { transition: opacity 0.08s ease, transform 0.08s ease; }
.pop-enter-from  { opacity: 0; transform: scale(0.95) translateY(-4px); }
.pop-leave-to    { opacity: 0; transform: scale(0.95) translateY(-4px); }

.edit-label {
  display: block;
  font-size: 0.8125rem;
  font-weight: 500;
  color: #374151;
  margin-bottom: 0.3rem;
}
.edit-input {
  display: block;
  width: 100%;
  border: 1px solid #d1d5db;
  border-radius: 0.5rem;
  padding: 0.45rem 0.65rem;
  font-size: 0.875rem;
  color: #1f2937;
  background: #fff;
  outline: none;
  transition: border-color 0.15s;
}
.edit-input:focus {
  border-color: rgb(254,80,103);
  box-shadow: 0 0 0 3px rgba(254,80,103,0.1);
}
</style>
