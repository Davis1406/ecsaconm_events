<template>
  <div class="flex flex-col space-y-4 flex-1">
    <HeaderView :headerTitle="headerTitle" />

    <!-- Global messages -->
    <div v-if="successMsg" class="p-3 px-4 rounded-2xl text-sm bg-green-100 border border-green-400 text-green-800">{{ successMsg }}</div>
    <div v-if="errorMsg"   class="p-3 px-4 rounded-2xl text-sm bg-red-100 border border-red-400 text-red-800">{{ errorMsg }}</div>

    <!-- ── Tab bar ─────────────────────────────────────────────────────────── -->
    <div class="bg-white rounded-2xl shadow-sm overflow-hidden">
      <div class="flex overflow-x-auto border-b border-gray-100">

        <button @click="activeTab = 'abstracts'"
          class="flex items-center gap-2 px-5 py-3.5 text-sm font-semibold whitespace-nowrap border-b-2 transition"
          :class="activeTab === 'abstracts' ? 'border-pink-500 text-pink-600' : 'border-transparent text-gray-500 hover:text-gray-700'">
          <DocumentTextIcon class="w-4 h-4" />
          Accepted Abstracts
          <span v-if="abstractsTotal" class="ml-1 text-xs font-normal text-gray-400">({{ abstractsTotal }})</span>
        </button>

        <button @click="activeTab = 'templates'"
          class="flex items-center gap-2 px-5 py-3.5 text-sm font-semibold whitespace-nowrap border-b-2 transition"
          :class="activeTab === 'templates' ? 'border-pink-500 text-pink-600' : 'border-transparent text-gray-500 hover:text-gray-700'">
          <PresentationChartBarIcon class="w-4 h-4" />
          Presentation Templates
          <span v-if="templates.length" class="ml-1 text-xs font-normal text-gray-400">({{ templates.length }})</span>
        </button>

        <button @click="activeTab = 'reminders'"
          class="flex items-center gap-2 px-5 py-3.5 text-sm font-semibold whitespace-nowrap border-b-2 transition"
          :class="activeTab === 'reminders' ? 'border-pink-500 text-pink-600' : 'border-transparent text-gray-500 hover:text-gray-700'">
          <BellAlertIcon class="w-4 h-4" />
          Registration Reminders
        </button>

        <button @click="activeTab = 'uploads'"
          class="flex items-center gap-2 px-5 py-3.5 text-sm font-semibold whitespace-nowrap border-b-2 transition"
          :class="activeTab === 'uploads' ? 'border-pink-500 text-pink-600' : 'border-transparent text-gray-500 hover:text-gray-700'">
          <ArrowUpTrayIcon class="w-4 h-4" />
          Uploaded Presentations
          <span v-if="uploadsTotal" class="ml-1 text-xs font-normal text-gray-400">({{ uploadsTotal }})</span>
        </button>

      </div>
    </div>

    <!-- ══════════════════════════════════════════════════════════════════════ -->
    <!-- TAB 1 · Accepted Abstracts                                           -->
    <!-- ══════════════════════════════════════════════════════════════════════ -->
    <div v-if="activeTab === 'abstracts'" class="flex flex-col gap-4">

      <!-- ── Stat cards ───────────────────────────────────────────────────── -->
      <div class="grid grid-cols-2 sm:grid-cols-5 gap-3">

        <!-- Total -->
        <button @click="setAbstractFilter('all')"
          class="flex flex-col items-center justify-center gap-1 p-4 rounded-2xl shadow-sm border-2 transition"
          :class="abstractsFilter === 'all'
            ? 'border-pink-500 bg-pink-50'
            : 'border-transparent bg-white hover:border-gray-200'">
          <span class="text-2xl font-extrabold"
            :style="abstractsFilter === 'all' ? 'color:rgb(254,80,103)' : 'color:#1f2937'">
            {{ stats.total ?? '—' }}
          </span>
          <span class="text-xs font-semibold text-gray-500 uppercase tracking-wide">Total</span>
        </button>

        <!-- Oral -->
        <button @click="setAbstractFilter('oral')"
          class="flex flex-col items-center justify-center gap-1 p-4 rounded-2xl shadow-sm border-2 transition"
          :class="abstractsFilter === 'oral'
            ? 'border-blue-500 bg-blue-50'
            : 'border-transparent bg-white hover:border-gray-200'">
          <span class="text-2xl font-extrabold"
            :class="abstractsFilter === 'oral' ? 'text-blue-600' : 'text-gray-800'">
            {{ stats.oral ?? '—' }}
          </span>
          <span class="text-xs font-semibold text-gray-500 uppercase tracking-wide">Oral</span>
        </button>

        <!-- Poster -->
        <button @click="setAbstractFilter('poster')"
          class="flex flex-col items-center justify-center gap-1 p-4 rounded-2xl shadow-sm border-2 transition"
          :class="abstractsFilter === 'poster'
            ? 'border-purple-500 bg-purple-50'
            : 'border-transparent bg-white hover:border-gray-200'">
          <span class="text-2xl font-extrabold"
            :class="abstractsFilter === 'poster' ? 'text-purple-600' : 'text-gray-800'">
            {{ stats.poster ?? '—' }}
          </span>
          <span class="text-xs font-semibold text-gray-500 uppercase tracking-wide">Poster</span>
        </button>

        <!-- Unique Presenters -->
        <button @click="setAbstractFilter('presenters')"
          class="flex flex-col items-center justify-center gap-1 p-4 rounded-2xl shadow-sm border-2 transition"
          :class="abstractsFilter === 'presenters'
            ? 'border-green-500 bg-green-50'
            : 'border-transparent bg-white hover:border-gray-200'">
          <span class="text-2xl font-extrabold"
            :class="abstractsFilter === 'presenters' ? 'text-green-600' : 'text-gray-800'">
            {{ stats.unique_presenters ?? '—' }}
          </span>
          <span class="text-xs font-semibold text-gray-500 uppercase tracking-wide text-center leading-tight">Unique Presenters</span>
        </button>

        <!-- Multi-Presenters -->
        <button @click="setAbstractFilter('multi')"
          class="flex flex-col items-center justify-center gap-1 p-4 rounded-2xl shadow-sm border-2 transition"
          :class="abstractsFilter === 'multi'
            ? 'border-orange-500 bg-orange-50'
            : 'border-transparent bg-white hover:border-gray-200'">
          <span class="text-2xl font-extrabold"
            :class="abstractsFilter === 'multi' ? 'text-orange-500' : 'text-gray-800'">
            {{ stats.multi_presenters ?? '—' }}
          </span>
          <span class="text-xs font-semibold text-gray-500 uppercase tracking-wide text-center leading-tight">2+ Abstracts</span>
        </button>

      </div>

      <!-- ── Main card ─────────────────────────────────────────────────────── -->
      <div class="bg-white rounded-2xl shadow-sm overflow-hidden">

      <!-- Toolbar -->
      <div class="flex flex-wrap items-center gap-3 px-5 py-4 border-b border-gray-100">
        <h2 class="text-sm font-bold text-gray-700 flex-1">
          Accepted Abstracts
          <span v-if="abstractsFilter !== 'all'" class="ml-2 text-xs font-normal px-2 py-0.5 rounded-full"
            :class="{
              'bg-blue-100 text-blue-700': abstractsFilter === 'oral',
              'bg-purple-100 text-purple-700': abstractsFilter === 'poster',
              'bg-green-100 text-green-700': abstractsFilter === 'presenters',
              'bg-orange-100 text-orange-700': abstractsFilter === 'multi',
            }">
            {{ { oral:'Oral only', poster:'Poster only', presenters:'All (by presenter)', multi:'2+ abstracts' }[abstractsFilter] }}
            <button @click="setAbstractFilter('all')" class="ml-1 hover:opacity-70">✕</button>
          </span>
        </h2>
        <search-component @search="handleAbstractSearch" />
        <button @click="activeTab = 'reminders'"
          class="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-semibold text-white transition hover:opacity-90"
          style="background-color: rgb(254,80,103);">
          <BellAlertIcon class="w-4 h-4" />
          Send Reminders
        </button>
        <button @click="showImport = !showImport"
          class="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-semibold border-2 transition"
          style="border-color: rgb(254,80,103); color: rgb(254,80,103);">
          <ArrowUpTrayIcon class="w-4 h-4" />
          Import
        </button>
      </div>

      <!-- Import panel (collapsed by default) -->
      <div v-if="showImport" class="px-5 py-5 border-b border-gray-100 bg-gray-50 space-y-4">
        <h3 class="font-semibold text-gray-700">Import Abstracts from File</h3>
        <p class="text-sm text-gray-500">Upload an ODS or XLSX file exported from your abstract management system.</p>
        <div class="flex flex-col sm:flex-row gap-3 items-start sm:items-end">
          <div class="flex-1">
            <label class="block text-xs font-semibold text-gray-600 mb-1.5 uppercase tracking-wide">File (.xlsx or .ods)</label>
            <input type="file" accept=".xlsx,.ods,.xls" @change="onImportFileSelected" ref="importFileInput"
              class="block w-full text-sm text-gray-700 border border-gray-200 rounded-xl px-3 py-2
                     file:mr-4 file:py-1.5 file:px-4 file:rounded-full file:border-0
                     file:text-xs file:font-semibold file:text-white cursor-pointer" />
          </div>
          <div class="flex gap-2">
            <button @click="previewImport" :disabled="!importFile || importLoading"
              class="px-5 py-2 rounded-xl text-sm font-semibold border-2 transition disabled:opacity-50"
              style="border-color: rgb(254,80,103); color: rgb(254,80,103);">
              {{ importLoading ? 'Checking…' : 'Preview' }}
            </button>
            <button v-if="importPreview" @click="runImport" :disabled="importLoading"
              class="px-5 py-2 rounded-xl text-sm font-semibold text-white transition hover:opacity-90 disabled:opacity-50"
              style="background-color: rgb(254,80,103);">
              {{ importLoading ? 'Importing…' : 'Import' }}
            </button>
          </div>
        </div>
        <!-- Preview stats -->
        <div v-if="importPreview" class="flex flex-wrap gap-2 text-xs font-semibold">
          <span class="px-3 py-1.5 rounded-full bg-blue-100 text-blue-700">{{ importPreview.to_import }} to import</span>
          <span class="px-3 py-1.5 rounded-full bg-gray-100 text-gray-500">{{ importPreview.duplicates }} duplicates</span>
          <span class="px-3 py-1.5 rounded-full bg-green-100 text-green-700">{{ importPreview.with_accounts }} have accounts</span>
          <span class="px-3 py-1.5 rounded-full bg-yellow-100 text-yellow-700">{{ importPreview.without_accounts }} no account</span>
        </div>
        <div v-if="importResult" class="p-3 rounded-xl text-sm bg-green-50 border border-green-200 text-green-800">
          ✓ Imported {{ importResult.imported }} abstracts · {{ importResult.skipped_duplicates }} duplicates skipped
        </div>
      </div>

      <!-- Abstract list table -->
      <SpinnerComponent v-if="abstractsLoading" />
      <div v-else>
        <div class="flex bg-mercury-500 px-5 py-2 uppercase text-xs font-bold text-gray-500">
          <div class="w-5/12">Title</div>
          <div class="w-2/12">Event</div>
          <div class="w-2/12">Submitter</div>
          <div class="w-1/12">Type</div>
          <div class="w-1/12">Status</div>
          <div class="w-1/12">Date</div>
        </div>
        <div v-if="abstracts.length === 0" class="px-5 py-10 text-center text-sm text-gray-400 italic">No abstracts found.</div>
        <div v-for="a in abstracts" :key="a.id"
          class="flex sm:flex-row flex-col px-5 py-3 text-sm items-center border-t border-gray-100 cursor-pointer hover:bg-gray-50 transition"
          @click="$router.push({ name: 'Abstract', params: { id: a.id } })">
          <div class="sm:w-5/12 w-full font-medium text-gray-800 leading-snug pr-3">{{ a.title }}</div>
          <div class="sm:w-2/12 w-full text-xs text-gray-500 pr-2 leading-snug">{{ a.event }}</div>
          <div class="sm:w-2/12 w-full text-xs text-gray-600">{{ a.submitter_name }}</div>
          <div class="sm:w-1/12 w-full">
            <span class="text-xs px-2 py-0.5 rounded-full bg-gray-100 text-gray-600 capitalize">{{ a.presentation_type || '—' }}</span>
          </div>
          <div class="sm:w-1/12 w-full">
            <span :class="statusClass(a.status)" class="px-2 py-1 rounded-full text-xs font-semibold capitalize">{{ a.status }}</span>
          </div>
          <div class="sm:w-1/12 w-full text-xs text-gray-400">{{ formatDate(a.created_at) }}</div>
        </div>
      </div>

      <!-- Pagination -->
      <div class="px-5 py-3 border-t border-gray-100">
        <pagination-component :currentPage="abstractsPage" :totalPages="abstractsTotalPages" @page-change="handleAbstractPage" />
      </div>

      </div><!-- /main card -->
    </div><!-- /tab 1 -->

    <!-- ══════════════════════════════════════════════════════════════════════ -->
    <!-- TAB 2 · Presentation Templates                                       -->
    <!-- ══════════════════════════════════════════════════════════════════════ -->
    <div v-if="activeTab === 'templates'" class="bg-white rounded-2xl shadow-sm overflow-hidden">

      <!-- Toolbar -->
      <div class="flex flex-wrap items-center gap-3 px-5 py-4 border-b border-gray-100">
        <h2 class="text-sm font-bold text-gray-700 flex-1">Presentation Templates</h2>
        <button @click="showTemplateUpload = !showTemplateUpload"
          class="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-semibold text-white transition hover:opacity-90"
          style="background-color: rgb(254,80,103);">
          <ArrowUpTrayIcon class="w-4 h-4" />
          Upload Template
        </button>
      </div>

      <!-- Upload panel -->
      <div v-if="showTemplateUpload" class="px-5 py-5 border-b border-gray-100 bg-gray-50 space-y-4">
        <p class="text-sm text-gray-500">Upload a PowerPoint, Word or PDF template. Accepted: <strong>.ppt .pptx .doc .docx .pdf .zip</strong>. Max 50 MB.</p>
        <div class="grid sm:grid-cols-2 gap-4">
          <div>
            <label class="block text-xs font-semibold text-gray-600 mb-1.5 uppercase tracking-wide">File</label>
            <input type="file" accept=".ppt,.pptx,.doc,.docx,.pdf,.zip" @change="onTemplateFileSelected" ref="templateFileInput"
              class="block w-full text-sm border border-gray-200 rounded-xl px-3 py-2
                     file:mr-4 file:py-1.5 file:px-4 file:rounded-full file:border-0
                     file:text-xs file:font-semibold file:text-white cursor-pointer" />
          </div>
          <div>
            <label class="block text-xs font-semibold text-gray-600 mb-1.5 uppercase tracking-wide">Description (optional)</label>
            <input v-model="newTemplateDescription" type="text" placeholder="e.g. ECSACONM 2026 oral presentation template"
              class="w-full border border-gray-200 rounded-xl px-3 py-2 text-sm focus:outline-none" />
          </div>
        </div>
        <button @click="uploadTemplate" :disabled="!selectedTemplateFile || templateUploading"
          class="px-6 py-2 rounded-full text-sm font-semibold text-white disabled:opacity-50 transition hover:opacity-90"
          style="background-color: rgb(254,80,103);">
          {{ templateUploading ? 'Uploading…' : 'Upload' }}
        </button>
      </div>

      <!-- Template list -->
      <SpinnerComponent v-if="templatesLoading" />
      <div v-else>
        <div class="flex bg-mercury-500 px-5 py-2 uppercase text-xs font-bold text-gray-500">
          <div class="w-5/12">File Name</div>
          <div class="w-3/12">Description</div>
          <div class="w-2/12">Size</div>
          <div class="w-2/12">Actions</div>
        </div>
        <div v-if="templates.length === 0" class="px-5 py-10 text-center text-sm text-gray-400 italic">No templates uploaded yet.</div>
        <div v-for="tpl in templates" :key="tpl.id"
          class="flex sm:flex-row flex-col px-5 py-3 text-sm items-center border-t border-gray-100">
          <div class="sm:w-5/12 w-full font-medium text-gray-800">
            <span class="mr-2">{{ fileIcon(tpl.original_name) }}</span>{{ tpl.original_name }}
          </div>
          <div class="sm:w-3/12 w-full text-xs text-gray-500">{{ tpl.description || '—' }}</div>
          <div class="sm:w-2/12 w-full text-xs text-gray-400">{{ formatSize(tpl.file_size) }}</div>
          <div class="sm:w-2/12 w-full flex gap-2">
            <a :href="`${apiUrl}/presentation_templates/${tpl.id}/download`" target="_blank"
              class="px-3 py-1 text-xs rounded-full font-semibold text-white hover:opacity-90 transition"
              style="background-color: rgb(0,150,180);">
              Download
            </a>
            <button @click="deleteTemplate(tpl.id)"
              class="px-3 py-1 text-xs rounded-full font-semibold text-white bg-red-500 hover:bg-red-400 transition">
              Delete
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- ══════════════════════════════════════════════════════════════════════ -->
    <!-- TAB 3 · Registration Reminders                                       -->
    <!-- ══════════════════════════════════════════════════════════════════════ -->
    <div v-if="activeTab === 'reminders'" class="flex flex-col gap-4">

      <!-- Presenters list card -->
      <div class="bg-white rounded-2xl shadow-sm overflow-hidden">
        <div class="flex flex-wrap items-center gap-3 px-5 py-4 border-b border-gray-100">
          <h2 class="text-sm font-bold text-gray-700 flex-1">Registration Reminders</h2>
          <span class="text-xs text-gray-400">Send registration reminders to accepted presenters who haven't registered yet.</span>
        </div>
        <div class="px-5 py-6">
          <SpinnerComponent v-if="remindersLoading" />
          <div v-else>
            <div v-if="presenters.length === 0" class="py-8 text-center text-sm text-gray-400 italic">
              All presenters have registered, or no accepted abstracts found.
            </div>
            <div v-else>
              <p class="text-sm text-gray-600 mb-4">
                <strong>{{ presenters.length }}</strong> presenter{{ presenters.length !== 1 ? 's' : '' }} have not yet registered for the conference.
              </p>
              <div class="rounded-xl border border-gray-100 overflow-hidden mb-5">
                <div class="flex bg-mercury-500 px-4 py-2 uppercase text-xs font-bold text-gray-500">
                  <div class="w-4/12">Name</div>
                  <div class="w-4/12">Email</div>
                  <div class="w-4/12">Abstract</div>
                </div>
                <div v-for="p in presenters.slice(0, 10)" :key="p.abstract_id"
                  class="flex px-4 py-2.5 text-sm border-t border-gray-100">
                  <div class="w-4/12 font-medium text-gray-700">{{ [p.firstname, p.lastname].filter(Boolean).join(' ') || p.presenter_name || '—' }}</div>
                  <div class="w-4/12 text-xs text-gray-500">{{ p.email }}</div>
                  <div class="w-4/12 text-xs text-gray-400 truncate">{{ p.abstract_title }}</div>
                </div>
                <div v-if="presenters.length > 10" class="px-4 py-2 text-xs text-gray-400 border-t border-gray-100 italic">
                  … and {{ presenters.length - 10 }} more
                </div>
              </div>
              <div class="flex gap-3 flex-wrap">
                <button @click="sendReminders" :disabled="sendingReminders"
                  class="px-6 py-2.5 rounded-xl text-sm font-semibold text-white transition hover:opacity-90 disabled:opacity-50"
                  style="background-color: rgb(254,80,103);">
                  {{ sendingReminders ? 'Sending…' : `Send Reminders to All ${presenters.length}` }}
                </button>
                <router-link :to="{ name: 'AbstractNotifications' }"
                  class="px-6 py-2.5 rounded-xl text-sm font-semibold border-2 transition"
                  style="border-color: rgb(254,80,103); color: rgb(254,80,103);">
                  Advanced Options →
                </router-link>
              </div>
              <div v-if="reminderResult" class="mt-4 p-3 rounded-xl text-sm bg-green-50 border border-green-200 text-green-800">
                {{ reminderResult }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Email Template Editor card -->
      <div class="bg-white rounded-2xl shadow-sm overflow-hidden">
        <div class="flex flex-wrap items-center gap-3 px-5 py-4 border-b border-gray-100">
          <div class="flex-1">
            <h2 class="text-sm font-bold text-gray-700">Reminder Email Template</h2>
            <p class="text-xs text-gray-400 mt-0.5">Edit and preview the email sent to unregistered presenters.</p>
          </div>
          <div class="flex gap-2">
            <button @click="reminderTplPreview = !reminderTplPreview; if(reminderTplPreview && !reminderTpl.body_html) loadReminderTemplate()"
              class="flex items-center gap-1.5 px-4 py-2 rounded-xl text-sm font-semibold transition"
              :class="reminderTplPreview ? 'text-white' : 'text-gray-600 border border-gray-200 hover:bg-gray-50'"
              :style="reminderTplPreview ? 'background-color: rgb(254,80,103);' : ''">
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
              </svg>
              {{ reminderTplPreview ? 'Close Editor' : 'Preview / Edit Template' }}
            </button>
          </div>
        </div>

        <!-- Expanded editor -->
        <div v-if="reminderTplPreview" class="px-5 py-5 space-y-4">
          <!-- Loading -->
          <div v-if="reminderTplLoading" class="flex justify-center py-8">
            <svg class="animate-spin h-7 w-7" style="color: rgb(254,80,103);" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
            </svg>
          </div>

          <div v-else>
            <!-- Save feedback -->
            <div v-if="reminderTplSaved" class="p-3 rounded-xl bg-green-50 border border-green-200 text-green-700 text-sm mb-3">
              ✓ Template saved successfully.
            </div>
            <div v-if="reminderTplError" class="p-3 rounded-xl bg-red-50 border border-red-200 text-red-700 text-sm mb-3">
              {{ reminderTplError }}
            </div>

            <!-- Subject -->
            <div>
              <label class="block text-xs font-semibold text-gray-600 mb-1 uppercase tracking-wide">Email Subject</label>
              <input v-model="reminderTpl.subject" type="text"
                class="w-full px-3 py-2.5 border border-gray-200 rounded-xl text-sm focus:outline-none focus:border-pink-400" />
            </div>

            <!-- Toggle preview / HTML -->
            <div>
              <div class="flex items-center justify-between mb-2">
                <label class="text-xs font-semibold text-gray-600 uppercase tracking-wide">HTML Body</label>
                <button @click="reminderTplEditMode = reminderTplEditMode === 'edit' ? 'preview' : 'edit'"
                  class="text-xs px-3 py-1 rounded-lg border transition"
                  :class="reminderTplEditMode === 'preview'
                    ? 'border-pink-400 text-pink-600 bg-pink-50'
                    : 'border-gray-200 text-gray-500 hover:border-gray-300'">
                  {{ reminderTplEditMode === 'preview' ? '✎ Edit HTML' : '👁 Preview' }}
                </button>
              </div>

              <!-- Preview iframe -->
              <div v-if="reminderTplEditMode === 'preview'" class="border border-gray-200 rounded-xl overflow-hidden">
                <iframe :srcdoc="reminderTpl.body_html" style="width:100%; height:520px; border:none;"></iframe>
              </div>

              <!-- HTML editor -->
              <textarea v-else v-model="reminderTpl.body_html" rows="22"
                class="w-full px-3 py-2.5 border border-gray-200 rounded-xl text-sm font-mono focus:outline-none focus:border-pink-400"
                style="resize: vertical;"></textarea>

              <p class="text-xs text-gray-400 mt-1">
                Available variables (use double curly braces):
                <code class="bg-gray-100 px-1 rounded">firstname</code>
                <code class="bg-gray-100 px-1 rounded">event_name</code>
                <code class="bg-gray-100 px-1 rounded">abstract_title</code>
                <code class="bg-gray-100 px-1 rounded">has_account</code>
                <code class="bg-gray-100 px-1 rounded">year</code>
              </p>
            </div>

            <!-- Actions -->
            <div class="flex justify-end gap-3 pt-2 border-t border-gray-100">
              <button @click="reminderTplEditMode = 'preview'; reminderTpl.body_html = reminderTplOriginal.body_html; reminderTpl.subject = reminderTplOriginal.subject"
                class="px-5 py-2.5 border border-gray-200 rounded-xl text-sm font-semibold text-gray-600 hover:bg-gray-50 transition">
                Reset Changes
              </button>
              <button @click="saveReminderTemplate" :disabled="reminderTplSaving"
                class="px-6 py-2.5 rounded-xl text-sm font-semibold text-white transition hover:opacity-90 disabled:opacity-50"
                style="background-color: rgb(254,80,103);">
                {{ reminderTplSaving ? 'Saving…' : 'Save Template' }}
              </button>
            </div>
          </div>
        </div>
      </div>

    </div>

    <!-- ══════════════════════════════════════════════════════════════════════ -->
    <!-- TAB 4 · Uploaded Presentations                                       -->
    <!-- ══════════════════════════════════════════════════════════════════════ -->
    <div v-if="activeTab === 'uploads'" class="bg-white rounded-2xl shadow-sm overflow-hidden">

      <div class="flex flex-wrap items-center gap-3 px-5 py-4 border-b border-gray-100">
        <h2 class="text-sm font-bold text-gray-700 flex-1">Uploaded Presentations</h2>
        <search-component @search="handleUploadsSearch" />
        <span class="text-xs text-gray-400">{{ uploadsTotal }} file{{ uploadsTotal !== 1 ? 's' : '' }} uploaded</span>
      </div>

      <SpinnerComponent v-if="uploadsLoading" />
      <div v-else>
        <div class="flex bg-mercury-500 px-5 py-2 uppercase text-xs font-bold text-gray-500">
          <div class="w-4/12">Abstract Title</div>
          <div class="w-2/12">Presenter</div>
          <div class="w-3/12">Email</div>
          <div class="w-2/12">Uploaded</div>
          <div class="w-1/12">File</div>
        </div>
        <div v-if="uploads.length === 0" class="px-5 py-10 text-center text-sm text-gray-400 italic">No presentations uploaded yet.</div>
        <div v-for="u in uploads" :key="u.id"
          class="flex sm:flex-row flex-col px-5 py-3 text-sm items-center border-t border-gray-100 hover:bg-gray-50 transition">
          <div class="sm:w-4/12 w-full font-medium text-gray-800 leading-snug pr-3">
            <router-link :to="{ name: 'Abstract', params: { id: u.id } }" class="hover:underline" style="color: rgb(0,150,180);">
              {{ u.title }}
            </router-link>
          </div>
          <div class="sm:w-2/12 w-full text-xs text-gray-700">{{ u.presenting_author ? u.presenting_author.name : u.submitter_name }}</div>
          <div class="sm:w-3/12 w-full text-xs text-gray-400">{{ u.presenting_author ? u.presenting_author.email : u.submitter_email }}</div>
          <div class="sm:w-2/12 w-full text-xs text-gray-400">{{ formatDate(u.presentation_uploaded_at) }}</div>
          <div class="sm:w-1/12 w-full">
            <a :href="`${apiUrl}/abstracts/${u.id}/download-presentation`" target="_blank"
              class="inline-flex items-center gap-1 px-3 py-1 text-xs rounded-full font-semibold text-white hover:opacity-90 transition"
              style="background-color: rgb(0,150,180);">
              <ArrowDownTrayIcon class="h-3.5 w-3.5" />
              Get
            </a>
          </div>
        </div>
        <div class="px-5 py-3 border-t border-gray-100">
          <pagination-component :currentPage="uploadsPage" :totalPages="uploadsTotalPages" @page-change="handleUploadsPage" />
        </div>
      </div>
    </div>

  </div>
</template>

<script>
import HeaderView from '@/includes/Header.vue'
import SpinnerComponent from '@/components/Spinner.vue'
import PaginationComponent from '@/components/PaginationComponent.vue'
import SearchComponent from '@/components/SearchComponent.vue'
import { fetchData } from '@/services/apiService'
import { useAuthStore } from '@/store/authStore'
import axios from 'axios'
import {
  DocumentTextIcon, ArrowUpTrayIcon, ArrowDownTrayIcon,
} from '@heroicons/vue/24/outline'
import { PresentationChartBarIcon, BellAlertIcon } from '@heroicons/vue/24/solid'

export default {
  name: 'AbstractsView',
  components: {
    HeaderView, SpinnerComponent, PaginationComponent, SearchComponent,
    DocumentTextIcon, ArrowUpTrayIcon, ArrowDownTrayIcon,
    PresentationChartBarIcon, BellAlertIcon,
  },

  setup() {
    const authStore = useAuthStore()
    const raw = authStore.permissions || []
    const permissions = raw.map(p => (typeof p === 'string' ? p : p.permission_code))
    return { permissions, accessToken: authStore.accessToken }
  },

  data() {
    return {
      headerTitle: 'Abstracts',
      activeTab: 'abstracts',
      apiUrl: import.meta.env.VITE_API_URL,

      // ── Tab 1: Abstracts ──────────────────────────────────────────────────
      abstracts: [], abstractsLoading: true,
      abstractsPage: 1, abstractsPageSize: 20,
      abstractsTotal: 0, abstractsSearch: '',
      abstractsFilter: 'all',  // 'all' | 'oral' | 'poster' | 'presenters' | 'multi'
      stats: { total: null, oral: null, poster: null, unique_presenters: null, multi_presenters: null },
      showImport: false,
      importFile: null, importLoading: false,
      importPreview: null, importResult: null,

      // ── Tab 2: Templates ──────────────────────────────────────────────────
      templates: [], templatesLoading: true,
      showTemplateUpload: false,
      selectedTemplateFile: null, newTemplateDescription: '',
      templateUploading: false,

      // ── Tab 3: Reminders ──────────────────────────────────────────────────
      presenters: [], remindersLoading: false,
      sendingReminders: false, reminderResult: '',
      // Reminder template editor
      reminderTplPreview: false,
      reminderTplLoading: false,
      reminderTplSaving: false,
      reminderTplSaved: false,
      reminderTplError: '',
      reminderTplEditMode: 'preview', // 'preview' | 'edit'
      reminderTpl: { subject: '', body_html: '' },
      reminderTplOriginal: { subject: '', body_html: '' },

      // ── Tab 4: Uploads ────────────────────────────────────────────────────
      uploads: [], uploadsLoading: true,
      uploadsPage: 1, uploadsPageSize: 20,
      uploadsTotal: 0, uploadsSearch: '',

      successMsg: '', errorMsg: '',
    }
  },

  computed: {
    abstractsTotalPages() { return Math.max(1, Math.ceil(this.abstractsTotal / this.abstractsPageSize)) },
    uploadsTotalPages()   { return Math.max(1, Math.ceil(this.uploadsTotal / this.uploadsPageSize)) },
  },

  watch: {
    activeTab(tab) {
      if (tab === 'templates' && !this.templates.length && !this.templatesLoading) this.loadTemplates()
      if (tab === 'reminders' && !this.presenters.length) this.loadPresenters()
      if (tab === 'uploads'   && !this.uploads.length && !this.uploadsLoading) this.loadUploads()
    },
  },

  mounted() {
    this.loadAbstracts()
    this.loadStats()
    this.loadTemplates()
    this.loadUploads()
  },

  methods: {

    // ── Abstracts ─────────────────────────────────────────────────────────
    async loadStats() {
      try {
        const res = await axios.get(`${this.apiUrl}/abstracts/stats`, {
          headers: { Authorization: `Bearer ${this.accessToken}` },
        })
        this.stats = res.data
      } catch (e) { console.error('stats:', e) }
    },

    setAbstractFilter(filter) {
      this.abstractsFilter = filter
      this.abstractsPage = 1
      this.loadAbstracts()
    },

    async loadAbstracts() {
      this.abstractsLoading = true
      try {
        const skip = (this.abstractsPage - 1) * this.abstractsPageSize
        const params = {
          skip,
          limit: this.abstractsPageSize,
          status: 'accepted',
        }
        if (this.abstractsSearch) params.search = this.abstractsSearch
        if (this.abstractsFilter === 'oral')   params.presentation_type = 'oral'
        if (this.abstractsFilter === 'poster') params.presentation_type = 'poster'
        if (this.abstractsFilter === 'multi')  params.presenter_email = 'multi'
        // 'presenters' and 'all' → no extra filter, just show all accepted

        const res = await axios.get(`${this.apiUrl}/abstracts/`, {
          params,
          headers: { Authorization: `Bearer ${this.accessToken}` },
        })
        this.abstracts = res.data?.data || []
        this.abstractsTotal = res.data?.total || 0
      } catch (e) { console.error(e) }
      finally { this.abstractsLoading = false }
    },
    handleAbstractSearch(q) { this.abstractsSearch = q; this.abstractsPage = 1; this.loadAbstracts() },
    handleAbstractPage(p)   { this.abstractsPage = p; this.loadAbstracts() },

    onImportFileSelected(e) { this.importFile = e.target.files[0] || null; this.importPreview = null; this.importResult = null },

    async previewImport() {
      if (!this.importFile) return
      this.importLoading = true
      const form = new FormData(); form.append('file', this.importFile)
      try {
        const res = await axios.post(`${this.apiUrl}/abstracts/import-preview`, form, {
          headers: { Authorization: `Bearer ${this.accessToken}`, 'Content-Type': 'multipart/form-data' },
        })
        this.importPreview = res.data
      } catch (e) { this.errorMsg = e.response?.data?.detail || 'Preview failed' }
      finally { this.importLoading = false }
    },

    async runImport() {
      if (!this.importFile) return
      this.importLoading = true
      const form = new FormData(); form.append('file', this.importFile)
      try {
        const res = await axios.post(`${this.apiUrl}/abstracts/import`, form, {
          headers: { Authorization: `Bearer ${this.accessToken}`, 'Content-Type': 'multipart/form-data' },
        })
        this.importResult = res.data
        this.importPreview = null
        this.importFile = null
        if (this.$refs.importFileInput) this.$refs.importFileInput.value = ''
        this.loadAbstracts()
      } catch (e) { this.errorMsg = e.response?.data?.detail || 'Import failed' }
      finally { this.importLoading = false }
    },

    // ── Templates ─────────────────────────────────────────────────────────
    async loadTemplates() {
      this.templatesLoading = true
      try {
        const res = await axios.get(`${this.apiUrl}/presentation_templates`, {
          headers: { Authorization: `Bearer ${this.accessToken}` },
        })
        this.templates = res.data || []
      } catch (e) { console.error(e) }
      finally { this.templatesLoading = false }
    },

    onTemplateFileSelected(e) { this.selectedTemplateFile = e.target.files[0] || null },

    async uploadTemplate() {
      if (!this.selectedTemplateFile) return
      this.templateUploading = true
      this.successMsg = ''; this.errorMsg = ''
      const form = new FormData()
      form.append('file', this.selectedTemplateFile)
      form.append('description', this.newTemplateDescription)
      try {
        await axios.post(`${this.apiUrl}/presentation_templates`, form, {
          headers: { Authorization: `Bearer ${this.accessToken}`, 'Content-Type': 'multipart/form-data' },
        })
        this.successMsg = 'Template uploaded successfully.'
        this.selectedTemplateFile = null; this.newTemplateDescription = ''
        if (this.$refs.templateFileInput) this.$refs.templateFileInput.value = ''
        this.showTemplateUpload = false
        this.loadTemplates()
      } catch (e) { this.errorMsg = e.response?.data?.detail || 'Upload failed.' }
      finally { this.templateUploading = false }
    },

    async deleteTemplate(id) {
      if (!confirm('Delete this template?')) return
      try {
        await axios.delete(`${this.apiUrl}/presentation_templates/${id}`, {
          headers: { Authorization: `Bearer ${this.accessToken}` },
        })
        this.templates = this.templates.filter(t => t.id !== id)
      } catch (e) { this.errorMsg = 'Delete failed.' }
    },

    // ── Reminders ─────────────────────────────────────────────────────────
    async loadPresenters() {
      this.remindersLoading = true
      try {
        const res = await axios.get(`${this.apiUrl}/abstracts/registration-reminder-preview`, {
          headers: { Authorization: `Bearer ${this.accessToken}` },
        })
        this.presenters = Array.isArray(res.data) ? res.data : (res.data?.data || [])
      } catch (e) { console.error(e) }
      finally { this.remindersLoading = false }
    },

    async sendReminders() {
      this.sendingReminders = true; this.reminderResult = ''
      try {
        const res = await axios.post(`${this.apiUrl}/abstracts/send-registration-reminders`, {}, {
          headers: { Authorization: `Bearer ${this.accessToken}` },
        })
        this.reminderResult = res.data?.message || `Reminders sent to ${res.data?.sent || 0} presenters.`
        this.loadPresenters()
      } catch (e) { this.errorMsg = e.response?.data?.detail || 'Failed to send reminders.' }
      finally { this.sendingReminders = false }
    },

    async loadReminderTemplate() {
      this.reminderTplLoading = true
      this.reminderTplSaved = false
      this.reminderTplError = ''
      try {
        const res = await axios.get(`${this.apiUrl}/email_templates/registration_reminder`, {
          headers: { Authorization: `Bearer ${this.accessToken}` },
        })
        this.reminderTpl = { subject: res.data.subject || '', body_html: res.data.body_html || '' }
        this.reminderTplOriginal = { ...this.reminderTpl }
        this.reminderTplEditMode = 'preview'
      } catch (e) {
        this.reminderTplError = e.response?.data?.detail || 'Failed to load template.'
      } finally {
        this.reminderTplLoading = false
      }
    },

    async saveReminderTemplate() {
      this.reminderTplSaving = true
      this.reminderTplSaved = false
      this.reminderTplError = ''
      try {
        await axios.put(
          `${this.apiUrl}/email_templates/registration_reminder`,
          { subject: this.reminderTpl.subject, body_html: this.reminderTpl.body_html },
          { headers: { Authorization: `Bearer ${this.accessToken}` } }
        )
        this.reminderTplSaved = true
        this.reminderTplOriginal = { ...this.reminderTpl }
      } catch (e) {
        this.reminderTplError = e.response?.data?.detail || 'Failed to save template.'
      } finally {
        this.reminderTplSaving = false
      }
    },

    // ── Uploads ───────────────────────────────────────────────────────────
    async loadUploads() {
      this.uploadsLoading = true
      try {
        const skip = (this.uploadsPage - 1) * this.uploadsPageSize
        const res = await axios.get(`${this.apiUrl}/abstracts/uploaded-presentations/list`, {
          params: { skip, limit: this.uploadsPageSize, search: this.uploadsSearch },
          headers: { Authorization: `Bearer ${this.accessToken}` },
        })
        this.uploads = res.data.data || []
        this.uploadsTotal = res.data.total || 0
      } catch (e) { console.error(e) }
      finally { this.uploadsLoading = false }
    },
    handleUploadsSearch(q) { this.uploadsSearch = q; this.uploadsPage = 1; this.loadUploads() },
    handleUploadsPage(p)   { this.uploadsPage = p; this.loadUploads() },

    // ── Helpers ───────────────────────────────────────────────────────────
    formatDate(d) {
      if (!d) return '—'
      return new Date(d).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' })
    },
    statusClass(s) {
      return {
        submitted: 'bg-yellow-100 text-yellow-700', pending: 'bg-yellow-100 text-yellow-700',
        accepted: 'bg-green-100 text-green-700', approved: 'bg-green-100 text-green-700',
        rejected: 'bg-red-100 text-red-700', under_review: 'bg-blue-100 text-blue-700',
      }[s] || 'bg-gray-100 text-gray-600'
    },
    formatSize(b) {
      if (!b) return '—'
      if (b < 1024) return `${b} B`
      if (b < 1024 * 1024) return `${(b / 1024).toFixed(1)} KB`
      return `${(b / (1024 * 1024)).toFixed(1)} MB`
    },
    fileIcon(name) {
      const ext = (name || '').split('.').pop().toLowerCase()
      return { pptx: '📊', ppt: '📊', docx: '📄', doc: '📄', pdf: '📕', zip: '🗜️' }[ext] || '📎'
    },
  },
}
</script>
