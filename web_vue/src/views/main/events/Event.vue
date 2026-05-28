<template>
  <SpinnerComponent v-if="isLoading" />
  <div v-else class="flex flex-col space-y-5 flex-1">
    <HeaderView :headerTitle="headerTitle" />

    <!-- Event hero card -->
    <div class="bg-white rounded-2xl shadow-sm overflow-hidden">

      <!-- Banner image or gradient header -->
      <div class="relative h-44 overflow-hidden"
        :style="event.banner_image
          ? 'background: #000;'
          : 'background: linear-gradient(135deg, rgb(254,80,103) 0%, rgb(180,30,55) 100%);'">
        <img v-if="event.banner_image"
          :src="bannerUrl"
          alt="Event banner"
          class="w-full h-full object-cover opacity-70" />
        <div class="absolute inset-0 flex flex-col justify-end p-6">
          <h1 class="text-2xl sm:text-3xl font-bold text-white drop-shadow leading-tight">
            {{ event.event }}
          </h1>
          <p v-if="event.theme" class="text-white/80 text-sm mt-1 italic">{{ event.theme }}</p>
        </div>
        <!-- Edit button overlay -->
        <router-link :to="{ name: 'EditEvent', params: { id: id } }"
          class="absolute top-4 right-4 flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-white/20 backdrop-blur text-white hover:bg-white/30 transition border border-white/30">
          <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
          </svg>
          Edit
        </router-link>
      </div>

      <!-- Event metadata row -->
      <div class="px-6 py-4 flex flex-wrap gap-6 border-b border-gray-100">
        <div v-if="event.organiser" class="flex items-center gap-2 text-sm text-gray-600">
          <UserGroupIcon class="w-4 h-4 flex-shrink-0" style="color: rgb(254,80,103);" />
          <span>{{ event.organiser }}</span>
        </div>
        <div v-if="event.location" class="flex items-center gap-2 text-sm text-gray-600">
          <MapPinIcon class="w-4 h-4 flex-shrink-0" style="color: rgb(254,80,103);" />
          <span>{{ event.location }}</span>
        </div>
        <div v-if="event.start_date" class="flex items-center gap-2 text-sm text-gray-600">
          <CalendarDaysIcon class="w-4 h-4 flex-shrink-0" style="color: rgb(254,80,103);" />
          <span>{{ formatDate(event.start_date) }} – {{ formatDate(event.end_date) }}</span>
        </div>
      </div>

      <!-- Formatted Description -->
      <div v-if="event.description" class="px-6 py-5 border-b border-gray-50">
        <div class="space-y-3">
          <template v-for="(block, i) in descriptionBlocks" :key="i">
            <!-- Section heading (ALL CAPS or ends with colon) -->
            <p v-if="block.type === 'heading'"
              class="text-sm font-bold text-gray-800 uppercase tracking-wide mt-4 first:mt-0">
              {{ block.text }}
            </p>
            <!-- Bullet point -->
            <div v-else-if="block.type === 'bullet'" class="flex items-start gap-2">
              <span class="mt-1.5 flex-shrink-0 h-1.5 w-1.5 rounded-full" style="background-color: rgb(254,80,103);"></span>
              <p class="text-sm text-gray-600 leading-relaxed">{{ block.text }}</p>
            </div>
            <!-- Date line (contains a month name or numeric date pattern) -->
            <div v-else-if="block.type === 'date'"
              class="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium text-gray-700 bg-gray-50 border border-gray-100">
              <CalendarDaysIcon class="w-3.5 h-3.5 flex-shrink-0" style="color: rgb(254,80,103);" />
              {{ block.text }}
            </div>
            <!-- Normal paragraph -->
            <p v-else class="text-sm text-gray-600 leading-relaxed">{{ block.text }}</p>
          </template>
        </div>
      </div>

      <!-- Quick stats strip -->
      <div class="grid grid-cols-3 divide-x divide-gray-100 px-2">
        <div class="py-4 px-6 text-center">
          <p class="text-2xl font-bold text-gray-800">{{ participants.length }}</p>
          <p class="text-xs text-gray-400 uppercase tracking-wide mt-0.5">Participants</p>
        </div>
        <div class="py-4 px-6 text-center">
          <p class="text-2xl font-bold text-green-600">{{ paidCount }}</p>
          <p class="text-xs text-gray-400 uppercase tracking-wide mt-0.5">Paid</p>
        </div>
        <div class="py-4 px-6 text-center">
          <p class="text-2xl font-bold text-yellow-600">{{ participants.length - paidCount }}</p>
          <p class="text-xs text-gray-400 uppercase tracking-wide mt-0.5">Pending</p>
        </div>
      </div>
    </div>

    <!-- Tab navigation -->
    <div class="bg-white rounded-2xl shadow-sm overflow-hidden">
      <div class="flex overflow-x-auto border-b border-gray-100">
        <button @click="activeTab = 'participants'"
          class="flex items-center gap-2 px-5 py-3.5 text-sm font-semibold whitespace-nowrap border-b-2 transition"
          :class="activeTab === 'participants' ? 'border-pink-500 text-pink-600' : 'border-transparent text-gray-500 hover:text-gray-700'">
          <UsersIcon class="w-4 h-4" />
          Participants <span class="ml-1 text-xs font-normal text-gray-400">({{ participants.length }})</span>
        </button>
        <button @click="activeTab = 'documents'"
          class="flex items-center gap-2 px-5 py-3.5 text-sm font-semibold whitespace-nowrap border-b-2 transition"
          :class="activeTab === 'documents' ? 'border-pink-500 text-pink-600' : 'border-transparent text-gray-500 hover:text-gray-700'">
          <FolderOpenIcon class="w-4 h-4" />
          Documents <span class="ml-1 text-xs font-normal text-gray-400">({{ documents.length }})</span>
        </button>
        <button @click="activeTab = 'links'"
          class="flex items-center gap-2 px-5 py-3.5 text-sm font-semibold whitespace-nowrap border-b-2 transition"
          :class="activeTab === 'links' ? 'border-pink-500 text-pink-600' : 'border-transparent text-gray-500 hover:text-gray-700'">
          <LinkIcon class="w-4 h-4" />
          Links <span class="ml-1 text-xs font-normal text-gray-400">({{ links.length }})</span>
        </button>
        <button @click="activeTab = 'import'"
          class="flex items-center gap-2 px-5 py-3.5 text-sm font-semibold whitespace-nowrap border-b-2 transition"
          :class="activeTab === 'import' ? 'border-pink-500 text-pink-600' : 'border-transparent text-gray-500 hover:text-gray-700'">
          <ArrowUpTrayIcon class="w-4 h-4" />
          Import Participants
        </button>
      </div>
    </div>

    <!-- Participants section -->
    <div v-if="activeTab === 'participants'" class="bg-white rounded-2xl shadow-sm overflow-hidden">

      <!-- Toolbar -->
      <div class="flex flex-wrap items-center gap-3 px-5 py-4 border-b border-gray-100">
        <h2 class="text-sm font-bold text-gray-700 flex-1">Participants</h2>
        <search-component @search="handleSearch" />

        <!-- Visual Reports -->
        <button @click="showReportsModal = true"
          class="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-semibold border-2 transition"
          style="border-color: rgb(254,80,103); color: rgb(254,80,103);">
          <ChartBarIcon class="w-4 h-4" />
          Reports
        </button>

        <!-- Extract Report (Excel) -->
        <button @click="extractReport"
          class="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-semibold text-white transition hover:opacity-90"
          style="background-color: rgb(254,80,103);">
          <ArrowDownTrayIcon class="w-4 h-4" />
          Extract Report
        </button>

        <DownloadComponent v-if="permissions.includes('DOWNLOAD_PARTICIPANT_LIST')"
          @participants="handleParticipants" @paid="handlePaid" @notPaid="handleNotPaid"
          @attendance="handleAttendance" />
        <button v-if="permissions.includes('PRINT_BADGE')" @click="openPrintBadgesModal"
          class="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-semibold text-white transition hover:opacity-90"
          style="background-color: rgb(254,80,103);">
          <IdentificationIcon class="w-4 h-4" />
          Print Badges
        </button>
        <button v-if="permissions.includes('BULK_UPLOAD')" @click="openBulkUploadParticipantsModal"
          class="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-semibold border-2 transition"
          style="border-color: rgb(254,80,103); color: rgb(254,80,103);">
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
          </svg>
          Bulk Upload
        </button>
      </div>

      <!-- Alerts -->
      <div v-if="errorMsg" class="mx-5 mt-4 p-3 rounded-xl text-sm text-red-700 bg-red-50 border border-red-200">{{ errorMsg }}</div>
      <div v-if="successMsg" class="mx-5 mt-4 p-3 rounded-xl text-sm text-green-700 bg-green-50 border border-green-200">{{ successMsg }}</div>

      <!-- Table header -->
      <div class="hidden sm:grid grid-cols-12 gap-2 bg-gray-50 px-5 py-3 text-xs font-bold uppercase tracking-wider text-gray-500 border-b border-gray-100">
        <div class="col-span-4">Participant</div>
        <div class="col-span-2">Institution</div>
        <div class="col-span-2">Country</div>
        <div class="col-span-1 text-center">Paid</div>
        <div class="col-span-1 text-center">Proof</div>
        <div class="col-span-2 text-right">Actions</div>
      </div>

      <!-- Empty state -->
      <div v-if="participants.length === 0" class="py-16 text-center">
        <div class="h-14 w-14 rounded-full flex items-center justify-center mx-auto mb-4"
          style="background-color: rgba(254,80,103,0.1);">
          <UserGroupIcon class="w-7 h-7" style="color: rgb(254,80,103);" />
        </div>
        <p class="text-gray-400 text-sm">No participants yet.</p>
      </div>

      <!-- Rows -->
      <div v-for="(participant, index) in participants" :key="participant.id"
        class="flex sm:grid sm:grid-cols-12 gap-2 items-center px-5 py-3 border-b border-gray-50 hover:bg-gray-50 transition text-sm"
        :class="index % 2 === 0 ? '' : 'bg-gray-50/50'">

        <!-- Name — clickable link to participant profile -->
        <div class="col-span-4">
          <router-link
            v-if="participant.user_id"
            :to="{ name: 'User', params: { id: participant.user_id } }"
            class="font-medium hover:underline transition"
            style="color: rgb(254,80,103);">
            {{ [participant.title, participant.firstname, participant.lastname].filter(Boolean).join(' ') || '—' }}
          </router-link>
          <span v-else class="font-medium text-gray-800">
            {{ [participant.title, participant.firstname, participant.lastname].filter(Boolean).join(' ') || '—' }}
          </span>
        </div>

        <!-- Institution -->
        <div class="col-span-2 text-gray-500 text-xs truncate">{{ participant.organisation || participant.institution || '—' }}</div>

        <!-- Country -->
        <div class="col-span-2 text-gray-500 text-xs">{{ participant.country || '—' }}</div>

        <!-- Paid badge -->
        <div class="col-span-1 flex justify-center">
          <span v-if="paidStatus(participant.paid || participant.event_payment)"
            class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold bg-green-100 text-green-700">
            <CheckCircleIcon class="w-3.5 h-3.5" /> Yes
          </span>
          <span v-else class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold bg-red-100 text-red-600">
            <XCircleIcon class="w-3.5 h-3.5" /> No
          </span>
        </div>

        <!-- Payment Proof -->
        <div class="col-span-1 flex justify-center">
          <button v-if="participant.payment_proof" @click="viewProof(participant)"
            title="View Payment Proof"
            class="p-1.5 rounded-lg border border-blue-200 text-blue-500 hover:bg-blue-50 transition">
            <DocumentTextIcon class="w-4 h-4" />
          </button>
          <span v-else class="text-gray-300 text-xs">—</span>
        </div>

        <!-- Actions -->
        <div class="col-span-2 flex justify-end gap-2">
          <button @click="previewBadge(participant)"
            title="Preview Badge"
            class="p-1.5 rounded-lg border border-gray-200 text-gray-500 hover:border-pink-300 hover:text-pink-500 transition">
            <IdentificationIcon class="w-4 h-4" />
          </button>
          <!-- Send Receipt — only for paid participants -->
          <button v-if="paidStatus(participant.paid || participant.event_payment)"
            @click="openReceiptModal(participant)"
            title="Send Receipt"
            class="p-1.5 rounded-lg border border-gray-200 text-gray-500 hover:border-green-400 hover:text-green-600 transition">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
            </svg>
          </button>
          <button v-if="permissions.includes('CONFIRM_EVENT_PAYMENT') && !paidStatus(participant.paid || participant.event_payment)"
            @click="paymentModal(participant.id)" title="Confirm Payment"
            class="p-1.5 rounded-lg border border-green-200 text-green-600 hover:bg-green-50 transition">
            <CurrencyDollarIcon class="w-4 h-4" />
          </button>
          <button v-if="permissions.includes('CANCEL_EVENT_REGISTRATION') && registrationStatus(participant.confirm_attendance)"
            @click="cancelRegistration(participant.id)" title="Cancel Registration"
            class="p-1.5 rounded-lg border border-red-200 text-red-500 hover:bg-red-50 transition">
            <XCircleIcon class="w-4 h-4" />
          </button>
        </div>
      </div>

      <div class="px-5 pb-2">
        <pagination-component :currentPage="currentPage" :totalPages="totalPages" @page-change="handlePageChange" />
      </div>
    </div>

    <!-- ── Documents Tab ───────────────────────────── -->
    <div v-if="activeTab === 'documents'" class="bg-white rounded-2xl shadow-sm overflow-hidden">

      <!-- Upload form -->
      <div class="px-5 py-5 border-b border-gray-100">
        <p class="text-sm font-bold text-gray-700 mb-4">Upload Document</p>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div class="sm:col-span-2">
            <label class="block text-xs font-semibold text-gray-400 uppercase tracking-widest mb-1">File</label>
            <input ref="docFileInput" type="file" @change="handleDocFile"
              accept=".pdf,.doc,.docx,.ppt,.pptx,.xls,.xlsx"
              class="w-full text-sm text-gray-600 file:mr-3 file:py-1.5 file:px-3 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:text-white file:cursor-pointer file:bg-pink-500" />
          </div>
          <div>
            <label class="block text-xs font-semibold text-gray-400 uppercase tracking-widest mb-1">Document Name</label>
            <input v-model="docUpload.file_name" type="text" placeholder="e.g. Conference Abstracts"
              class="w-full border border-gray-200 rounded-xl px-3 py-2 text-sm focus:outline-none" />
          </div>
          <div>
            <label class="block text-xs font-semibold text-gray-400 uppercase tracking-widest mb-1">Type</label>
            <select v-model="docUpload.doc_type"
              class="w-full border border-gray-200 rounded-xl px-3 py-2 text-sm focus:outline-none bg-white">
              <option value="abstract">Abstract Book</option>
              <option value="timetable">Timetable / Programme</option>
              <option value="poster">Poster</option>
              <option value="presentation">Presentation</option>
              <option value="other">Other</option>
            </select>
          </div>
          <div>
            <label class="block text-xs font-semibold text-gray-400 uppercase tracking-widest mb-1">Access Level</label>
            <select v-model="docUpload.access_level"
              class="w-full border border-gray-200 rounded-xl px-3 py-2 text-sm focus:outline-none bg-white">
              <option value="public">Public</option>
              <option value="registered">Registered Participants</option>
              <option value="admin">Admin Only</option>
            </select>
          </div>
        </div>

        <!-- Alerts -->
        <div v-if="docError" class="mt-3 p-3 rounded-xl text-sm text-red-700 bg-red-50 border border-red-200">{{ docError }}</div>
        <div v-if="docSuccess" class="mt-3 p-3 rounded-xl text-sm text-green-700 bg-green-50 border border-green-200">{{ docSuccess }}</div>

        <button @click="uploadDocument" :disabled="docUploading || !docFile"
          class="mt-4 inline-flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-semibold text-white transition hover:opacity-90 disabled:opacity-50"
          style="background-color: rgb(254,80,103);">
          <svg v-if="docUploading" class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
          </svg>
          <ArrowUpTrayIcon v-else class="w-4 h-4" />
          {{ docUploading ? 'Uploading…' : 'Upload Document' }}
        </button>
      </div>

      <!-- Documents list -->
      <div v-if="documents.length > 0" class="divide-y divide-gray-50">
        <div v-for="doc in documents" :key="doc.id"
          class="flex items-center gap-3 px-5 py-3.5 hover:bg-gray-50 transition">
          <div class="h-9 w-9 rounded-lg flex items-center justify-center flex-shrink-0"
            style="background-color: rgba(254,80,103,0.1);">
            <DocumentTextIcon class="w-5 h-5" style="color: rgb(254,80,103);" />
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-sm font-semibold text-gray-800 truncate">{{ doc.name || doc.file_name || 'Document' }}</p>
            <p class="text-xs text-gray-400 capitalize">{{ doc.document_type || doc.doc_type }} · {{ doc.access_level }}</p>
          </div>
          <a :href="docFileUrl(doc)" target="_blank"
            class="px-3 py-1.5 rounded-lg text-xs font-semibold border-2 transition"
            style="border-color: rgb(254,80,103); color: rgb(254,80,103);">
            View
          </a>
          <button @click="deleteDocument(doc.id)"
            class="p-1.5 rounded-lg border border-red-200 text-red-500 hover:bg-red-50 transition">
            <TrashIcon class="w-4 h-4" />
          </button>
        </div>
      </div>
      <div v-else class="py-16 text-center">
        <div class="h-14 w-14 rounded-full flex items-center justify-center mx-auto mb-4"
          style="background-color: rgba(254,80,103,0.08);">
          <FolderOpenIcon class="w-7 h-7" style="color: rgb(254,80,103);" />
        </div>
        <p class="text-gray-400 text-sm">No documents uploaded yet.</p>
      </div>
    </div>

    <!-- ── Links Tab ────────────────────────────────── -->
    <div v-if="activeTab === 'links'" class="bg-white rounded-2xl shadow-sm overflow-hidden">

      <!-- Add link form -->
      <div class="px-5 py-5 border-b border-gray-100">
        <p class="text-sm font-bold text-gray-700 mb-4">Add Link</p>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div>
            <label class="block text-xs font-semibold text-gray-400 uppercase tracking-widest mb-1">Name</label>
            <input v-model="newLink.name" type="text" placeholder="e.g. Photo Gallery, Video Recording"
              class="w-full border border-gray-200 rounded-xl px-3 py-2 text-sm focus:outline-none" />
          </div>
          <div>
            <label class="block text-xs font-semibold text-gray-400 uppercase tracking-widest mb-1">URL</label>
            <input v-model="newLink.link" type="url" placeholder="https://…"
              class="w-full border border-gray-200 rounded-xl px-3 py-2 text-sm focus:outline-none" />
          </div>
        </div>

        <!-- Alerts -->
        <div v-if="linkError" class="mt-3 p-3 rounded-xl text-sm text-red-700 bg-red-50 border border-red-200">{{ linkError }}</div>
        <div v-if="linkSuccess" class="mt-3 p-3 rounded-xl text-sm text-green-700 bg-green-50 border border-green-200">{{ linkSuccess }}</div>

        <button @click="addLink" :disabled="linkSaving || !newLink.name.trim() || !newLink.link.trim()"
          class="mt-4 inline-flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-semibold text-white transition hover:opacity-90 disabled:opacity-50"
          style="background-color: rgb(254,80,103);">
          <svg v-if="linkSaving" class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
          </svg>
          <LinkIcon v-else class="w-4 h-4" />
          Add Link
        </button>
      </div>

      <!-- Links list -->
      <div v-if="links.length > 0" class="divide-y divide-gray-50">
        <div v-for="link in links" :key="link.id"
          class="px-5 py-3.5 hover:bg-gray-50 transition">

          <!-- Edit mode -->
          <div v-if="editingLink && editingLink.id === link.id" class="flex flex-wrap items-center gap-2">
            <input v-model="editingLink.name" type="text"
              class="flex-1 min-w-[120px] border border-gray-200 rounded-lg px-2.5 py-1.5 text-sm focus:outline-none" />
            <input v-model="editingLink.link" type="url"
              class="flex-1 min-w-[180px] border border-gray-200 rounded-lg px-2.5 py-1.5 text-sm focus:outline-none" />
            <button @click="saveEditLink" :disabled="linkSaving"
              class="px-3 py-1.5 rounded-lg text-xs font-semibold text-white disabled:opacity-50"
              style="background-color: rgb(254,80,103);">Save</button>
            <button @click="cancelEditLink"
              class="px-3 py-1.5 rounded-lg text-xs font-semibold border border-gray-200 text-gray-600">Cancel</button>
          </div>

          <!-- View mode -->
          <div v-else class="flex items-center gap-3">
            <div class="h-9 w-9 rounded-lg flex items-center justify-center flex-shrink-0"
              style="background-color: rgba(254,80,103,0.1);">
              <LinkIcon class="w-5 h-5" style="color: rgb(254,80,103);" />
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-semibold text-gray-800">{{ link.name }}</p>
              <a :href="link.link" target="_blank"
                class="text-xs text-blue-500 hover:underline truncate block max-w-xs">{{ link.link }}</a>
            </div>
            <a :href="link.link" target="_blank"
              class="px-3 py-1.5 rounded-lg text-xs font-semibold border-2 transition"
              style="border-color: rgb(254,80,103); color: rgb(254,80,103);">
              Open
            </a>
            <button @click="startEditLink(link)"
              class="p-1.5 rounded-lg border border-gray-200 text-gray-500 hover:border-blue-300 hover:text-blue-500 transition">
              <PencilIcon class="w-4 h-4" />
            </button>
            <button @click="deleteLink(link.id)"
              class="p-1.5 rounded-lg border border-red-200 text-red-500 hover:bg-red-50 transition">
              <TrashIcon class="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
      <div v-else class="py-16 text-center">
        <div class="h-14 w-14 rounded-full flex items-center justify-center mx-auto mb-4"
          style="background-color: rgba(254,80,103,0.08);">
          <LinkIcon class="w-7 h-7" style="color: rgb(254,80,103);" />
        </div>
        <p class="text-gray-400 text-sm">No links added yet.</p>
        <p class="text-gray-300 text-xs mt-1">Add links to photo galleries, videos, or other resources.</p>
      </div>
    </div>

    <!-- ── Import Participants Tab ───────────────────── -->
    <div v-if="activeTab === 'import'" class="bg-white rounded-2xl shadow-sm overflow-hidden">
      <div class="px-5 py-5">
        <p class="text-sm font-bold text-gray-700 mb-1">Import Participants from Excel</p>
        <p class="text-xs text-gray-400 mb-5">Upload an <code>.xlsx</code> file with participant data. The system will map the columns automatically.</p>

        <!-- Column mapping reference -->
        <div class="mb-5 p-4 bg-gray-50 rounded-xl border border-gray-100">
          <p class="text-xs font-bold uppercase tracking-widest text-gray-400 mb-3">Expected Column Names</p>
          <div class="grid grid-cols-2 sm:grid-cols-3 gap-2 text-xs text-gray-600">
            <div><span class="font-semibold">First Name</span> → firstname</div>
            <div><span class="font-semibold">Last Name</span> → lastname</div>
            <div><span class="font-semibold">Title</span> → title</div>
            <div><span class="font-semibold">Designation (…)</span> → designation</div>
            <div><span class="font-semibold">Country</span> → country</div>
            <div><span class="font-semibold">Delegate Valid Email…</span> → email</div>
            <div><span class="font-semibold">Telephone</span> → phone</div>
            <div><span class="font-semibold">Participation Category</span> → category</div>
            <div><span class="font-semibold">Amount Paid</span> → paid (if > 0)</div>
          </div>
        </div>

        <!-- File picker -->
        <div class="mb-4">
          <label class="block text-xs font-semibold text-gray-400 uppercase tracking-widest mb-1">Excel File (.xlsx or .csv)</label>
          <input ref="importFileInput" type="file" @change="handleImportFile"
            accept=".xlsx,.csv,.xls"
            class="w-full text-sm text-gray-600" />
        </div>

        <!-- Selected file preview -->
        <div v-if="importFileName"
          class="mb-4 flex items-center gap-3 p-3 bg-blue-50 border border-blue-100 rounded-xl text-sm">
          <DocumentTextIcon class="w-5 h-5 text-blue-400 flex-shrink-0" />
          <div>
            <p class="font-semibold text-blue-800">{{ importFileName }}</p>
            <p class="text-xs text-blue-500">Ready to import</p>
          </div>
        </div>

        <!-- Alerts -->
        <div v-if="importError" class="mb-4 p-3 rounded-xl text-sm text-red-700 bg-red-50 border border-red-200">{{ importError }}</div>
        <div v-if="importSuccess" class="mb-4 p-3 rounded-xl text-sm text-green-700 bg-green-50 border border-green-200">{{ importSuccess }}</div>

        <button @click="uploadImport" :disabled="importUploading || !importFile"
          class="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-semibold text-white transition hover:opacity-90 disabled:opacity-50"
          style="background-color: rgb(254,80,103);">
          <svg v-if="importUploading" class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
          </svg>
          <ArrowUpTrayIcon v-else class="w-4 h-4" />
          {{ importUploading ? 'Importing…' : 'Start Import' }}
        </button>
      </div>
    </div>

    <!-- Modals -->
    <participant-modal :show="showParticipantModal" @confirmed="confirmParticipant" @closed="cancelParticipant"
      :event="event" :participant="participant" @file-uploaded="refreshItems" />
    <payment-modal :show="showPaymentModal" @paid="confirmPayment" @cancel="cancelPaymentModal"
      :userID="userID" :eventID="eventID" />
    <badge-modal :show="showBadgeModal" @close="closeBadgeModal" :participant="participant" :event_id="id" :event="event" />
    <print-badges-modal :show="showPrintBadgesModal" @close="closePrintBadgesModal"
      :participants="participants" :event_id="id" />
    <bulk-upload-participants-modal :show="showBulkUploadParticipantsModal" @close="closeBulkUploadParticipantsModal"
      :eventID="eventID" />
    <receipt-modal :show="showReceiptModal" @close="showReceiptModal = false"
      :participant="participant" :event="event" />

    <!-- Payment Proof Modal -->
    <div v-if="showProofModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <div class="bg-white rounded-2xl shadow-xl w-full max-w-2xl max-h-[90vh] flex flex-col overflow-hidden">
        <div class="flex items-center justify-between px-5 py-4 border-b border-gray-100">
          <h3 class="font-semibold text-gray-800">Payment Proof</h3>
          <button @click="showProofModal = false" class="text-gray-400 hover:text-gray-600 transition">
            <XCircleIcon class="w-6 h-6" />
          </button>
        </div>
        <div class="flex-1 overflow-auto p-5">
          <div v-if="proofUrl">
            <!-- Image proof -->
            <img v-if="isProofImage" :src="proofUrl" class="max-w-full rounded-xl mx-auto" alt="Payment Proof" />
            <!-- PDF proof — embedded inline -->
            <div v-else>
              <iframe :src="proofUrl" class="w-full rounded-xl border border-gray-200"
                style="height: 520px;" title="Payment Proof PDF"></iframe>
              <a :href="proofUrl" target="_blank"
                class="inline-flex items-center gap-1.5 mt-3 text-xs font-semibold hover:underline"
                style="color: rgb(254,80,103);">
                <DocumentTextIcon class="w-4 h-4" />
                Open in new tab
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Visual Reports Modal -->
    <div v-if="showReportsModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <div class="bg-white rounded-2xl shadow-xl w-full max-w-2xl max-h-[90vh] flex flex-col overflow-hidden">

        <!-- Header -->
        <div class="flex items-center justify-between px-5 py-4 border-b border-gray-100">
          <div class="flex items-center gap-2">
            <ChartBarIcon class="w-5 h-5" style="color: rgb(254,80,103);" />
            <h3 class="font-bold text-gray-800">Registration Reports</h3>
          </div>
          <div class="flex items-center gap-3">
            <button @click="extractReport"
              class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold text-white transition hover:opacity-90"
              style="background-color: rgb(254,80,103);">
              <ArrowDownTrayIcon class="w-3.5 h-3.5" />
              Export Excel
            </button>
            <button @click="showReportsModal = false" class="text-gray-400 hover:text-gray-600 transition">
              <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        <div class="flex-1 overflow-y-auto p-5 space-y-6">

          <!-- Payment Status -->
          <div>
            <p class="text-xs font-bold uppercase tracking-widest text-gray-400 mb-3">Payment Status</p>
            <div class="grid grid-cols-3 gap-3 mb-4">
              <div class="text-center p-3 rounded-xl bg-gray-50">
                <p class="text-2xl font-bold text-gray-800">{{ participants.length }}</p>
                <p class="text-xs text-gray-400 mt-0.5">Total</p>
              </div>
              <div class="text-center p-3 rounded-xl bg-green-50">
                <p class="text-2xl font-bold text-green-600">{{ paidCount }}</p>
                <p class="text-xs text-gray-400 mt-0.5">Paid</p>
              </div>
              <div class="text-center p-3 rounded-xl bg-yellow-50">
                <p class="text-2xl font-bold text-yellow-600">{{ participants.length - paidCount }}</p>
                <p class="text-xs text-gray-400 mt-0.5">Pending</p>
              </div>
            </div>
            <!-- Bar chart -->
            <div class="space-y-2" v-if="participants.length > 0">
              <div class="flex items-center gap-3">
                <span class="text-xs text-gray-500 w-16 text-right flex-shrink-0">Paid</span>
                <div class="flex-1 bg-gray-100 rounded-full h-5 overflow-hidden">
                  <div class="h-full rounded-full bg-green-500 transition-all duration-500 flex items-center justify-end pr-2"
                    :style="{ width: (paidCount / participants.length * 100) + '%' }">
                    <span v-if="paidCount > 0" class="text-white text-xs font-bold">{{ Math.round(paidCount / participants.length * 100) }}%</span>
                  </div>
                </div>
                <span class="text-xs font-semibold text-gray-600 w-8">{{ paidCount }}</span>
              </div>
              <div class="flex items-center gap-3">
                <span class="text-xs text-gray-500 w-16 text-right flex-shrink-0">Pending</span>
                <div class="flex-1 bg-gray-100 rounded-full h-5 overflow-hidden">
                  <div class="h-full rounded-full bg-yellow-400 transition-all duration-500 flex items-center justify-end pr-2"
                    :style="{ width: ((participants.length - paidCount) / participants.length * 100) + '%' }">
                    <span v-if="(participants.length - paidCount) > 0" class="text-white text-xs font-bold">{{ Math.round((participants.length - paidCount) / participants.length * 100) }}%</span>
                  </div>
                </div>
                <span class="text-xs font-semibold text-gray-600 w-8">{{ participants.length - paidCount }}</span>
              </div>
            </div>
          </div>

          <!-- By Category / Role -->
          <div v-if="categoryStats.length > 0">
            <p class="text-xs font-bold uppercase tracking-widest text-gray-400 mb-3">By Category</p>
            <div class="space-y-2">
              <div v-for="cat in categoryStats" :key="cat.label" class="flex items-center gap-3">
                <span class="text-xs text-gray-500 w-28 text-right flex-shrink-0 truncate">{{ cat.label }}</span>
                <div class="flex-1 bg-gray-100 rounded-full h-5 overflow-hidden">
                  <div class="h-full rounded-full transition-all duration-500 flex items-center justify-end pr-2"
                    :style="{ width: (cat.count / participants.length * 100) + '%', backgroundColor: 'rgb(254,80,103)' }">
                    <span v-if="cat.count > 0" class="text-white text-xs font-bold">{{ Math.round(cat.count / participants.length * 100) }}%</span>
                  </div>
                </div>
                <span class="text-xs font-semibold text-gray-600 w-8">{{ cat.count }}</span>
              </div>
            </div>
          </div>

          <!-- By Country (top 10) -->
          <div v-if="countryStats.length > 0">
            <p class="text-xs font-bold uppercase tracking-widest text-gray-400 mb-3">By Country <span class="normal-case font-normal">(top 10)</span></p>
            <div class="space-y-2">
              <div v-for="c in countryStats" :key="c.label" class="flex items-center gap-3">
                <span class="text-xs text-gray-500 w-28 text-right flex-shrink-0 truncate">{{ c.label }}</span>
                <div class="flex-1 bg-gray-100 rounded-full h-5 overflow-hidden">
                  <div class="h-full rounded-full transition-all duration-500 flex items-center justify-end pr-2"
                    :style="{ width: (c.count / countryStats[0].count * 100) + '%', backgroundColor: 'rgb(100,120,200)' }">
                    <span v-if="c.count > 0" class="text-white text-xs font-bold">{{ c.count }}</span>
                  </div>
                </div>
                <span class="text-xs font-semibold text-gray-600 w-8">{{ c.count }}</span>
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>

  </div>
</template>

<script>
import axios from 'axios';
import { fetchItem, createItem } from "@/services/apiService";
import {
  MapPinIcon, CalendarDaysIcon, UserGroupIcon, CheckCircleIcon,
  XCircleIcon, CurrencyDollarIcon, IdentificationIcon, DocumentTextIcon,
  ChartBarIcon, ArrowDownTrayIcon, LinkIcon, FolderOpenIcon,
  TrashIcon, PencilIcon, ArrowUpTrayIcon, UsersIcon,
} from '@heroicons/vue/24/solid';

import HeaderView from '@/includes/Header.vue';
import SpinnerComponent from "@/components/Spinner.vue";
import { useAuthStore } from "@/store/authStore";
import PaginationComponent from '@/components/PaginationComponent.vue';
import SearchComponent from '@/components/SearchComponent.vue';
import ParticipantModal from '@/components/ParticipantModal.vue';
import DownloadComponent from '@/components/DownloadComponent.vue';
import { exportToExcel } from '@/utils/exportToExcel';
import PaymentModal from "@/components/PaymentModal.vue";
import BadgeModal from "@/components/BadgeModal.vue";
import PrintBadgesModal from "@/components/PrintBadgesModal.vue";
import BulkUploadParticipantsModal from "@/components/BulkUploadParticipantsModal.vue";
import ReceiptModal from "@/components/ReceiptModal.vue";

const API_URL = import.meta.env.VITE_API_URL

const DATE_RE = /\b(\d{1,2}[\/-]\d{1,2}[\/-]\d{2,4}|\d{4}[\/-]\d{1,2}[\/-]\d{1,2}|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2},?\s+\d{4}|\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4})\b/i;
const CATEGORY_MAP = {
  member_state: 'Member State', participant: 'Participant', other_africa: 'Other Africa',
  world: 'International', student: 'Student', exhibitor: 'Exhibitor',
  secretariat: 'Secretariat', delegate: 'Delegate', presenter: 'Presenter',
  speaker: 'Speaker', sponsor: 'Sponsor', moderator: 'Moderator', moh: 'Ministry of Health',
};

export default {
  name: "EventView",
  components: {
    MapPinIcon, CalendarDaysIcon, UserGroupIcon, CheckCircleIcon, XCircleIcon,
    CurrencyDollarIcon, IdentificationIcon, DocumentTextIcon, ChartBarIcon, ArrowDownTrayIcon,
    LinkIcon, FolderOpenIcon, TrashIcon, PencilIcon, ArrowUpTrayIcon, UsersIcon,
    HeaderView, SpinnerComponent,
    PaginationComponent, SearchComponent, ParticipantModal, DownloadComponent,
    PaymentModal, BadgeModal, PrintBadgesModal, BulkUploadParticipantsModal, ReceiptModal,
  },
  data() {
    return {
      headerTitle: "Event Details",
      id: this.$route.params.id,
      isLoading: true,
      event: {},
      participants: [],
      participant: {},
      attendance: [],
      allParticipants: [],
      showParticipantModal: false,
      currentPage: 1,
      totalPages: "",
      pageSize: 10000,
      searchPhrase: "",
      showPaymentModal: false,
      userID: "",
      eventID: "",
      message: "",
      UserEventData: { user_id: "", event_id: "" },
      showBadgeModal: false,
      showPrintBadgesModal: false,
      showBulkUploadParticipantsModal: false,
      showReceiptModal: false,
      successMsg: "",
      errorMsg: "",
      showProofModal: false,
      proofUrl: '',
      showReportsModal: false,
      // Tabs
      activeTab: 'participants',
      // Documents
      documents: [],
      docFile: null,
      docUpload: { file_name: '', doc_type: 'abstract', access_level: 'public' },
      docUploading: false,
      docSuccess: '',
      docError: '',
      // Links
      links: [],
      newLink: { name: '', link: '' },
      editingLink: null,
      linkSaving: false,
      linkSuccess: '',
      linkError: '',
      // Import Participants
      importFile: null,
      importFileName: '',
      importUploading: false,
      importSuccess: '',
      importError: '',
      importPreviewCount: 0,
    };
  },
  mounted() {
    this.getEvent();
  },
  setup() {
    const authStore = useAuthStore();
    const raw = authStore.permissions || [];
    const permissions = raw.map(p => typeof p === "string" ? p : p.permission_code);
    return { permissions, authStore };
  },
  computed: {
    paidCount() {
      return this.participants.filter(p => this.paidStatus(p.paid || p.event_payment)).length;
    },
    bannerUrl() {
      if (!this.event.banner_image) return '';
      const base = import.meta.env.VITE_API_URL || '';
      return base.replace(/\/api\/?$/, '') + '/' + this.event.banner_image;
    },
    isProofImage() {
      if (!this.proofUrl) return false;
      return /\.(jpg|jpeg|png|gif|webp)(\?|$)/i.test(this.proofUrl);
    },
    descriptionBlocks() {
      if (!this.event.description) return [];
      const lines = this.event.description
        .split(/\n/)
        .map(l => l.trim())
        .filter(l => l.length > 0);
      return lines.map(line => {
        // Bullet: starts with •, -, *, or numbered list
        if (/^[•\-\*]\s+/.test(line) || /^\d+[\.\)]\s+/.test(line)) {
          return { type: 'bullet', text: line.replace(/^[•\-\*\d\.\)]+\s*/, '') };
        }
        // Heading: ALL CAPS (3+ words) or ends with colon and is short
        if (/^[A-Z][A-Z\s\d:&/-]{8,}$/.test(line) || (line.endsWith(':') && line.length < 60 && !/[a-z]{3}/.test(line))) {
          return { type: 'heading', text: line.replace(/:$/, '') };
        }
        // Date line
        if (DATE_RE.test(line) && line.length < 100) {
          return { type: 'date', text: line };
        }
        return { type: 'paragraph', text: line };
      });
    },
    categoryStats() {
      const counts = {};
      this.participants.forEach(p => {
        const raw = p.participant_category || p.participation_role || 'Unknown';
        const label = CATEGORY_MAP[raw] || raw || 'Unknown';
        counts[label] = (counts[label] || 0) + 1;
      });
      return Object.entries(counts)
        .map(([label, count]) => ({ label, count }))
        .sort((a, b) => b.count - a.count);
    },
    countryStats() {
      const counts = {};
      this.participants.forEach(p => {
        const c = p.country || 'Unknown';
        counts[c] = (counts[c] || 0) + 1;
      });
      return Object.entries(counts)
        .map(([label, count]) => ({ label, count }))
        .sort((a, b) => b.count - a.count)
        .slice(0, 10);
    },
  },
  methods: {
    async getEvent(silent = false) {
      if (!silent) this.isLoading = true;
      try {
        const response = await fetchItem("events", this.id, this.currentPage, this.pageSize, this.searchPhrase);
        this.event = response.event;
        this.participants = response.data || response.participants || [];
        this.attendance = response.attendance || [];
        this.totalPages = response.pages || 1;
        this.documents = response.event?.documents || [];
        this.links = response.event?.links || [];
      } catch (error) {
        console.error("Error fetching event:", error);
      } finally {
        this.isLoading = false;
      }
    },
    async handleSearch(searchQuery) {
      this.searchPhrase = searchQuery;
      this.getEvent();
    },
    async handlePageChange(newPage) {
      this.currentPage = newPage;
      this.getEvent();
    },
    paidStatus(status) { return status === true; },
    registrationStatus(status) { return status === true; },
    formatDate(dateString) {
      if (!dateString) return '';
      return new Date(dateString).toLocaleDateString("en-GB", { day: "2-digit", month: "short", year: "numeric" });
    },
    showParticipant(participant) {
      this.participant = participant;
      this.showParticipantModal = true;
    },
    confirmParticipant() { this.getEvent(); this.showParticipantModal = false; },
    cancelParticipant() { this.showParticipantModal = false; },
    refreshItems() { this.getEvent(); },
    handleParticipants() {
      this.getEvent();
      exportToExcel(this.participants, 'AllParticipants');
    },
    handlePaid() {
      this.getEvent();
      exportToExcel(this.participants.filter(p => p.paid || p.event_payment), 'PaidParticipants');
    },
    handleNotPaid() {
      this.getEvent();
      exportToExcel(this.participants.filter(p => !p.paid && !p.event_payment), 'NotPaidParticipants');
    },
    handleAttendance() {
      this.getEvent();
      exportToExcel(this.attendance, 'AttendanceRegister');
    },
    extractReport() {
      const rows = this.participants.map(p => ({
        'ID': p.id,
        'Title': p.title || '',
        'First Name': p.firstname || '',
        'Last Name': p.lastname || '',
        'Designation': p.designation || '',
        'Email': p.email || '',
        'Phone': p.phone || '',
        'Organisation': p.organisation || p.institution || '',
        'Country': p.country || '',
        'Category': CATEGORY_MAP[p.participant_category || p.participation_role] || p.participant_category || p.participation_role || '',
        'Paid': this.paidStatus(p.paid || p.event_payment) ? 'Yes' : 'No',
        'Payment Proof': p.payment_proof ? 'Yes' : 'No',
        'Registered': p.confirm_attendance ? 'Yes' : 'No',
      }));
      exportToExcel(rows, `EventReport_${this.event.event || this.id}`);
    },
    paymentModal(userID) {
      this.userID = userID;
      this.eventID = this.id;
      this.showPaymentModal = true;
    },
    confirmPayment() {
      this.message = "Payment confirmation was successful";
      this.showPaymentModal = false;
      this.getEvent();
    },
    cancelPaymentModal() { this.showPaymentModal = false; },
    async cancelRegistration(user_id) {
      this.UserEventData = { user_id, event_id: Number(this.id) };
      this.isLoading = true;
      try {
        await createItem("events/cancel_registration/", this.UserEventData);
        this.getEvent();
        this.errorMsg = "";
        this.successMsg = "Successfully cancelled registration for participant #" + user_id;
      } catch (error) {
        this.successMsg = "";
        this.errorMsg = error.response?.data?.detail || "Failed to cancel registration.";
      } finally {
        this.isLoading = false;
      }
    },
    previewBadge(participant) {
      this.participant = participant;
      this.showBadgeModal = true;
    },
    closeBadgeModal() { this.showBadgeModal = false; },
    openPrintBadgesModal() { this.showPrintBadgesModal = true; },
    closePrintBadgesModal() { this.showPrintBadgesModal = false; },
    openReceiptModal(participant) {
      this.participant = participant;
      this.showReceiptModal = true;
    },
    openBulkUploadParticipantsModal() {
      this.eventID = this.id;
      this.showBulkUploadParticipantsModal = true;
    },
    closeBulkUploadParticipantsModal() {
      this.getEvent();
      this.showBulkUploadParticipantsModal = false;
    },
    viewProof(participant) {
      const apiUrl = import.meta.env.VITE_API_URL || '';
      this.proofUrl = `${apiUrl}/${participant.payment_proof}`;
      this.showProofModal = true;
    },

    // ── Documents ──────────────────────────────────────
    handleDocFile(e) {
      this.docFile = e.target.files[0] || null;
      if (this.docFile && !this.docUpload.file_name) {
        this.docUpload.file_name = this.docFile.name.replace(/\.[^.]+$/, '');
      }
    },
    async uploadDocument() {
      if (!this.docFile) return;
      this.docUploading = true; this.docError = ''; this.docSuccess = '';
      try {
        const token = this.authStore.accessToken;
        const form = new FormData();
        form.append('file', this.docFile);
        form.append('file_name', this.docUpload.file_name || this.docFile.name);
        form.append('doc_type', this.docUpload.doc_type);
        form.append('access_level', this.docUpload.access_level);
        form.append('event_id', this.id);
        const api = axios.create({ baseURL: API_URL });
        if (token) api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        await api.post('/events/upload_document/', form);
        this.docFile = null;
        this.docUpload = { file_name: '', doc_type: 'abstract', access_level: 'public' };
        this.$refs.docFileInput && (this.$refs.docFileInput.value = '');
        this.docSuccess = 'Document uploaded successfully.';
        setTimeout(() => { this.docSuccess = ''; }, 3500);
        await this.getEvent(true);
      } catch (e) {
        this.docError = e.response?.data?.detail || 'Failed to upload document.';
      } finally {
        this.docUploading = false;
      }
    },
    async deleteDocument(docId) {
      if (!confirm('Delete this document?')) return;
      try {
        const token = this.authStore.accessToken;
        const api = axios.create({ baseURL: API_URL });
        if (token) api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        await api.delete(`/events/delete_document/${docId}`);
        await this.getEvent(true);
      } catch (e) {
        this.docError = e.response?.data?.detail || 'Failed to delete document.';
      }
    },
    docFileUrl(doc) {
      return `${API_URL}/${doc.path || doc.file_path || doc.file}`;
    },

    // ── Links ──────────────────────────────────────────
    async addLink() {
      if (!this.newLink.name.trim() || !this.newLink.link.trim()) return;
      this.linkSaving = true; this.linkError = ''; this.linkSuccess = '';
      try {
        const token = this.authStore.accessToken;
        const api = axios.create({ baseURL: API_URL });
        if (token) api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        await api.post('/events/add_link/', {
          event_id: parseInt(this.id),
          name: this.newLink.name,
          link: this.newLink.link,
        });
        this.newLink = { name: '', link: '' };
        this.linkSuccess = 'Link added.';
        setTimeout(() => { this.linkSuccess = ''; }, 3000);
        await this.getEvent(true);
      } catch (e) {
        this.linkError = e.response?.data?.detail || 'Failed to add link.';
      } finally {
        this.linkSaving = false;
      }
    },
    startEditLink(link) {
      this.editingLink = { ...link };
    },
    cancelEditLink() {
      this.editingLink = null;
    },
    async saveEditLink() {
      if (!this.editingLink) return;
      this.linkSaving = true; this.linkError = '';
      try {
        const token = this.authStore.accessToken;
        const api = axios.create({ baseURL: API_URL });
        if (token) api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        await api.put(`/events/update_link/${this.editingLink.id}`, {
          event_id: parseInt(this.id),
          name: this.editingLink.name,
          link: this.editingLink.link,
        });
        this.editingLink = null;
        this.linkSuccess = 'Link updated.';
        setTimeout(() => { this.linkSuccess = ''; }, 3000);
        await this.getEvent(true);
      } catch (e) {
        this.linkError = e.response?.data?.detail || 'Failed to update link.';
      } finally {
        this.linkSaving = false;
      }
    },
    async deleteLink(linkId) {
      if (!confirm('Delete this link?')) return;
      try {
        const token = this.authStore.accessToken;
        const api = axios.create({ baseURL: API_URL });
        if (token) api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        await api.delete(`/events/delete_link/${linkId}`);
        await this.getEvent(true);
      } catch (e) {
        this.linkError = e.response?.data?.detail || 'Failed to delete link.';
      }
    },

    // ── Import Participants ────────────────────────────
    handleImportFile(e) {
      this.importFile = e.target.files[0] || null;
      this.importFileName = this.importFile?.name || '';
      this.importPreviewCount = 0;
      this.importSuccess = '';
      this.importError = '';
    },
    async uploadImport() {
      if (!this.importFile) return;
      this.importUploading = true; this.importError = ''; this.importSuccess = '';
      try {
        const token = this.authStore.accessToken;
        const form = new FormData();
        form.append('file', this.importFile);
        form.append('eventID', this.id);
        const api = axios.create({ baseURL: API_URL });
        if (token) api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        const res = await api.post('/events/upload_participants/', form);
        const d = res.data
        const parts = []
        if (d.created) parts.push(`${d.created} new`)
        if (d.updated) parts.push(`${d.updated} updated`)
        if (d.skipped) parts.push(`${d.skipped} skipped`)
        this.importSuccess = `Import complete! ${parts.join(', ') || '0 rows'} (${d.total_processed} processed).`
        if (d.errors && d.errors.length > 0) {
          this.importError = 'Warnings: ' + d.errors.join(' | ')
        }
        this.importFile = null;
        this.importFileName = '';
        this.$refs.importFileInput && (this.$refs.importFileInput.value = '');
        // Refresh participants list
        this.getEvent(true);
      } catch (e) {
        this.importError = e.response?.data?.detail || 'Import failed. Check your file format and try again.';
      } finally {
        this.importUploading = false;
      }
    },
  }
};
</script>
