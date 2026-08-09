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

      <!-- ── Stat cards row 1: abstract counts ──────────────────────────── -->
      <div class="grid grid-cols-2 sm:grid-cols-5 gap-3">

        <button @click="setAbstractFilter('all')"
          class="flex flex-col items-center justify-center gap-1 p-4 rounded-2xl shadow-sm border-2 transition"
          :class="abstractsFilter === 'all' ? 'border-pink-500 bg-pink-50' : 'border-transparent bg-white hover:border-gray-200'">
          <span class="text-2xl font-extrabold" :style="abstractsFilter === 'all' ? 'color:rgb(254,80,103)' : 'color:#1f2937'">{{ stats.total ?? '—' }}</span>
          <span class="text-xs font-semibold text-gray-500 uppercase tracking-wide">Total</span>
        </button>

        <button @click="setAbstractFilter('oral')"
          class="flex flex-col items-center justify-center gap-1 p-4 rounded-2xl shadow-sm border-2 transition"
          :class="abstractsFilter === 'oral' ? 'border-blue-500 bg-blue-50' : 'border-transparent bg-white hover:border-gray-200'">
          <span class="text-2xl font-extrabold" :class="abstractsFilter === 'oral' ? 'text-blue-600' : 'text-gray-800'">{{ stats.oral ?? '—' }}</span>
          <span class="text-xs font-semibold text-gray-500 uppercase tracking-wide">Oral</span>
        </button>

        <button @click="setAbstractFilter('poster')"
          class="flex flex-col items-center justify-center gap-1 p-4 rounded-2xl shadow-sm border-2 transition"
          :class="abstractsFilter === 'poster' ? 'border-purple-500 bg-purple-50' : 'border-transparent bg-white hover:border-gray-200'">
          <span class="text-2xl font-extrabold" :class="abstractsFilter === 'poster' ? 'text-purple-600' : 'text-gray-800'">{{ stats.poster ?? '—' }}</span>
          <span class="text-xs font-semibold text-gray-500 uppercase tracking-wide">Poster</span>
        </button>

        <button @click="setAbstractFilter('presenters')"
          class="flex flex-col items-center justify-center gap-1 p-4 rounded-2xl shadow-sm border-2 transition"
          :class="abstractsFilter === 'presenters' ? 'border-green-500 bg-green-50' : 'border-transparent bg-white hover:border-gray-200'">
          <span class="text-2xl font-extrabold" :class="abstractsFilter === 'presenters' ? 'text-green-600' : 'text-gray-800'">{{ stats.unique_presenters ?? '—' }}</span>
          <span class="text-xs font-semibold text-gray-500 uppercase tracking-wide text-center leading-tight">Unique Presenters</span>
        </button>

        <button @click="setAbstractFilter('multi')"
          class="flex flex-col items-center justify-center gap-1 p-4 rounded-2xl shadow-sm border-2 transition"
          :class="abstractsFilter === 'multi' ? 'border-orange-500 bg-orange-50' : 'border-transparent bg-white hover:border-gray-200'">
          <span class="text-2xl font-extrabold" :class="abstractsFilter === 'multi' ? 'text-orange-500' : 'text-gray-800'">{{ stats.multi_presenters ?? '—' }}</span>
          <span class="text-xs font-semibold text-gray-500 uppercase tracking-wide text-center leading-tight">2+ Abstracts</span>
        </button>

      </div>

      <!-- ── Stat cards row 2: registration / payment ─────────────────────── -->
      <div class="grid grid-cols-3 gap-3">

        <button @click="setAbstractFilter('registered')"
          class="flex flex-col items-center justify-center gap-1 p-3 rounded-2xl shadow-sm border-2 transition"
          :class="abstractsFilter === 'registered' ? 'border-teal-500 bg-teal-50' : 'border-transparent bg-white hover:border-gray-200'">
          <span class="text-xl font-extrabold" :class="abstractsFilter === 'registered' ? 'text-teal-600' : 'text-gray-800'">{{ stats.registered ?? '—' }}</span>
          <span class="text-xs font-semibold text-gray-500 uppercase tracking-wide text-center leading-tight">✓ Registered</span>
        </button>

        <button @click="setAbstractFilter('not_registered')"
          class="flex flex-col items-center justify-center gap-1 p-3 rounded-2xl shadow-sm border-2 transition"
          :class="abstractsFilter === 'not_registered' ? 'border-red-400 bg-red-50' : 'border-transparent bg-white hover:border-gray-200'">
          <span class="text-xl font-extrabold" :class="abstractsFilter === 'not_registered' ? 'text-red-500' : 'text-gray-800'">{{ stats.not_registered ?? '—' }}</span>
          <span class="text-xs font-semibold text-gray-500 uppercase tracking-wide text-center leading-tight">✗ Not Registered</span>
        </button>

        <button @click="setAbstractFilter('paid')"
          class="flex flex-col items-center justify-center gap-1 p-3 rounded-2xl shadow-sm border-2 transition"
          :class="abstractsFilter === 'paid' ? 'border-emerald-500 bg-emerald-50' : 'border-transparent bg-white hover:border-gray-200'">
          <span class="text-xl font-extrabold" :class="abstractsFilter === 'paid' ? 'text-emerald-600' : 'text-gray-800'">{{ stats.paid ?? '—' }}</span>
          <span class="text-xs font-semibold text-gray-500 uppercase tracking-wide text-center leading-tight">💳 Paid</span>
        </button>

      </div>

      <!-- ── Main card ─────────────────────────────────────────────────────── -->
      <div class="bg-white rounded-2xl shadow-sm overflow-hidden">

      <!-- Toolbar -->
      <div class="flex flex-wrap items-center gap-3 px-5 py-4 border-b border-gray-100">
        <h2 class="text-sm font-bold text-gray-700 flex-1 flex items-center gap-2">
          Accepted Abstracts
          <span v-if="abstractsTotal" class="text-xs font-normal text-gray-400">({{ abstractsTotal }})</span>
          <span v-if="abstractsFilter !== 'all'" class="text-xs font-semibold px-2 py-0.5 rounded-full flex items-center gap-1"
            :class="{
              'bg-blue-100 text-blue-700': abstractsFilter === 'oral',
              'bg-purple-100 text-purple-700': abstractsFilter === 'poster',
              'bg-green-100 text-green-700': abstractsFilter === 'presenters',
              'bg-orange-100 text-orange-700': abstractsFilter === 'multi',
              'bg-teal-100 text-teal-700': abstractsFilter === 'registered',
              'bg-red-100 text-red-600': abstractsFilter === 'not_registered',
              'bg-emerald-100 text-emerald-700': abstractsFilter === 'paid',
            }">
            {{ { oral:'Oral only', poster:'Poster only', presenters:'All (by presenter)', multi:'2+ abstracts', registered:'Registered', not_registered:'Not Registered', paid:'Paid' }[abstractsFilter] }}
            <button @click="setAbstractFilter('all')" class="hover:opacity-70">✕</button>
          </span>
        </h2>
        <!-- Page size picker -->
        <select v-model.number="abstractsPageSize" @change="abstractsPage = 1; loadAbstracts()"
          class="px-2 py-1.5 text-xs border border-gray-200 rounded-lg text-gray-600 focus:outline-none">
          <option :value="25">25 / page</option>
          <option :value="50">50 / page</option>
          <option :value="100">100 / page</option>
        </select>
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
        <!-- Table header with sortable columns -->
        <div class="hidden sm:flex bg-mercury-500 px-5 py-2 uppercase text-xs font-bold text-gray-500 select-none">
          <div class="w-8 flex-shrink-0 text-center">#</div>
          <div class="flex-1 pl-3 cursor-pointer flex items-center gap-1 hover:text-gray-700 transition"
            @click="setSort('title')">
            Title
            <span class="text-gray-300">
              <svg v-if="abstractsSort.field === 'title'" class="w-3 h-3" :class="abstractsSort.dir === 'asc' ? 'text-pink-500' : 'text-pink-500'" fill="currentColor" viewBox="0 0 20 20">
                <path v-if="abstractsSort.dir === 'asc'" d="M10 3l7 7H3l7-7z"/>
                <path v-else d="M10 17l7-7H3l7 7z"/>
              </svg>
              <svg v-else class="w-3 h-3 opacity-30" fill="currentColor" viewBox="0 0 20 20"><path d="M10 3l7 7H3l7-7zM10 17l7-7H3l7 7z"/></svg>
            </span>
          </div>
          <div class="w-3/12 cursor-pointer flex items-center gap-1 hover:text-gray-700 transition"
            @click="setSort('presenter')">
            Presenter
            <span>
              <svg v-if="abstractsSort.field === 'presenter'" class="w-3 h-3 text-pink-500" fill="currentColor" viewBox="0 0 20 20">
                <path v-if="abstractsSort.dir === 'asc'" d="M10 3l7 7H3l7-7z"/>
                <path v-else d="M10 17l7-7H3l7 7z"/>
              </svg>
              <svg v-else class="w-3 h-3 opacity-30" fill="currentColor" viewBox="0 0 20 20"><path d="M10 3l7 7H3l7-7zM10 17l7-7H3l7 7z"/></svg>
            </span>
          </div>
          <div class="w-2/12 cursor-pointer flex items-center gap-1 hover:text-gray-700 transition"
            @click="setSort('type')">
            Type
            <span>
              <svg v-if="abstractsSort.field === 'type'" class="w-3 h-3 text-pink-500" fill="currentColor" viewBox="0 0 20 20">
                <path v-if="abstractsSort.dir === 'asc'" d="M10 3l7 7H3l7-7z"/>
                <path v-else d="M10 17l7-7H3l7 7z"/>
              </svg>
              <svg v-else class="w-3 h-3 opacity-30" fill="currentColor" viewBox="0 0 20 20"><path d="M10 3l7 7H3l7-7zM10 17l7-7H3l7 7z"/></svg>
            </span>
          </div>
          <div class="w-2/12 cursor-pointer flex items-center gap-1 hover:text-gray-700 transition"
            @click="setSort('created_at')">
            Date
            <span>
              <svg v-if="abstractsSort.field === 'created_at'" class="w-3 h-3 text-pink-500" fill="currentColor" viewBox="0 0 20 20">
                <path v-if="abstractsSort.dir === 'asc'" d="M10 3l7 7H3l7-7z"/>
                <path v-else d="M10 17l7-7H3l7 7z"/>
              </svg>
              <svg v-else class="w-3 h-3 opacity-30" fill="currentColor" viewBox="0 0 20 20"><path d="M10 3l7 7H3l7-7zM10 17l7-7H3l7 7z"/></svg>
            </span>
          </div>
        </div>

        <div v-if="abstracts.length === 0" class="px-5 py-10 text-center text-sm text-gray-400 italic">No abstracts found.</div>
        <div v-for="(a, idx) in sortedAbstracts" :key="a.id"
          class="flex sm:flex-row flex-col px-5 py-3 text-sm items-start sm:items-center border-t border-gray-100 cursor-pointer hover:bg-gray-50 transition group"
          @click="$router.push({ name: 'Abstract', params: { id: a.id } })">
          <!-- Row number -->
          <div class="hidden sm:flex w-8 flex-shrink-0 justify-center text-xs text-gray-300 group-hover:text-gray-400 font-mono tabular-nums">
            {{ (abstractsPage - 1) * abstractsPageSize + idx + 1 }}
          </div>
          <!-- Title -->
          <div class="flex-1 sm:pl-3 font-medium text-gray-800 leading-snug pr-3">
            {{ a.title }}
          </div>
          <!-- Presenter -->
          <div class="sm:w-3/12 w-full text-xs text-gray-600 pr-2 mt-1 sm:mt-0">
            <span class="sm:hidden text-gray-400 mr-1">Presenter:</span>
            <span class="font-medium">{{ presenterName(a) }}</span>
            <!-- Registration / payment badge -->
            <template v-if="presenterEmail(a) && presenterStatus(a)">
              <span v-if="presenterStatus(a).has_paid"
                class="ml-1.5 inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-700 whitespace-nowrap">
                💳 Paid
              </span>
              <span v-else-if="presenterStatus(a).has_registered"
                class="ml-1.5 inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded-full text-[10px] font-bold bg-teal-100 text-teal-700 whitespace-nowrap">
                ✓ Registered
              </span>
              <span v-else
                class="ml-1.5 inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded-full text-[10px] font-bold bg-red-100 text-red-600 whitespace-nowrap">
                ✗ Not Registered
              </span>
            </template>
            <div v-if="presenterEmail(a)" class="text-gray-400 truncate mt-0.5">{{ presenterEmail(a) }}</div>
          </div>
          <!-- Type badge -->
          <div class="sm:w-2/12 w-full mt-1 sm:mt-0">
            <span v-if="a.presentation_type === 'oral'"
              class="text-xs px-2 py-0.5 rounded-full font-semibold bg-blue-100 text-blue-700 capitalize">
              {{ a.presentation_type }}
            </span>
            <span v-else-if="a.presentation_type === 'poster'"
              class="text-xs px-2 py-0.5 rounded-full font-semibold bg-purple-100 text-purple-700 capitalize">
              {{ a.presentation_type }}
            </span>
            <span v-else class="text-xs text-gray-400">—</span>
          </div>
          <!-- Date -->
          <div class="sm:w-2/12 w-full text-xs text-gray-400 mt-1 sm:mt-0">{{ formatDate(a.created_at) }}</div>
          <!-- Edit icon -->
          <div class="sm:w-8 flex-shrink-0 flex justify-end">
            <button @click.stop="openEditModal(a)" title="Edit abstract"
              class="p-1.5 rounded-lg text-gray-300 hover:text-blue-500 hover:bg-blue-50 transition opacity-0 group-hover:opacity-100">
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
              </svg>
            </button>
          </div>
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

  <!-- ══════════════════════════════════════════════════════════════════════ -->
  <!-- Edit Abstract Modal                                                   -->
  <!-- ══════════════════════════════════════════════════════════════════════ -->
  <Teleport to="body">
    <div v-if="editModal.open"
      class="fixed inset-0 z-50 flex items-center justify-center p-4"
      @click.self="closeEditModal">
      <!-- Backdrop -->
      <div class="absolute inset-0 bg-black/40 backdrop-blur-sm" @click="closeEditModal"></div>

      <!-- Panel -->
      <div class="relative w-full max-w-2xl bg-white rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">

        <!-- Modal header -->
        <div class="flex items-center justify-between px-6 py-4 border-b border-gray-100 flex-shrink-0">
          <h2 class="font-semibold text-gray-800 text-base truncate pr-4">Edit Abstract</h2>
          <button @click="closeEditModal" class="p-1.5 rounded-lg text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition">
            <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>

        <!-- Scrollable body -->
        <div class="overflow-y-auto flex-1 px-6 py-5 space-y-4">

          <!-- Save feedback -->
          <div v-if="editModal.successMsg" class="p-3 rounded-xl bg-green-50 border border-green-200 text-green-700 text-sm">
            ✓ {{ editModal.successMsg }}
          </div>
          <div v-if="editModal.errorMsg" class="p-3 rounded-xl bg-red-50 border border-red-200 text-red-700 text-sm">
            {{ editModal.errorMsg }}
          </div>

          <!-- Title -->
          <div>
            <label class="block text-xs font-semibold text-gray-600 uppercase tracking-wide mb-1">Title</label>
            <input v-model="editModal.form.title" type="text"
              class="w-full px-3 py-2.5 border border-gray-200 rounded-xl text-sm focus:outline-none focus:border-blue-400 focus:ring-1 focus:ring-blue-400" />
          </div>

          <!-- Type + Status row -->
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-xs font-semibold text-gray-600 uppercase tracking-wide mb-1">Presentation Type</label>
              <select v-model="editModal.form.presentation_type"
                class="w-full px-3 py-2.5 border border-gray-200 rounded-xl text-sm focus:outline-none focus:border-blue-400 focus:ring-1 focus:ring-blue-400">
                <option value="oral">Oral</option>
                <option value="poster">Poster</option>
                <option value="either">Either</option>
              </select>
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-600 uppercase tracking-wide mb-1">Status</label>
              <select v-model="editModal.form.status"
                class="w-full px-3 py-2.5 border border-gray-200 rounded-xl text-sm focus:outline-none focus:border-blue-400 focus:ring-1 focus:ring-blue-400">
                <option value="submitted">Submitted</option>
                <option value="under_review">Under Review</option>
                <option value="accepted">Accepted</option>
                <option value="rejected">Rejected</option>
                <option value="revision_required">Revision Required</option>
              </select>
            </div>
          </div>

          <!-- Track -->
          <div>
            <label class="block text-xs font-semibold text-gray-600 uppercase tracking-wide mb-1">Track</label>
            <input v-model="editModal.form.track" type="text" placeholder="e.g. Maternal Health"
              class="w-full px-3 py-2.5 border border-gray-200 rounded-xl text-sm focus:outline-none focus:border-blue-400 focus:ring-1 focus:ring-blue-400" />
          </div>

          <!-- Keywords -->
          <div>
            <label class="block text-xs font-semibold text-gray-600 uppercase tracking-wide mb-1">Keywords</label>
            <input v-model="editModal.form.keywords" type="text" placeholder="Comma-separated"
              class="w-full px-3 py-2.5 border border-gray-200 rounded-xl text-sm focus:outline-none focus:border-blue-400 focus:ring-1 focus:ring-blue-400" />
          </div>

          <!-- Abstract body -->
          <div>
            <label class="block text-xs font-semibold text-gray-600 uppercase tracking-wide mb-1">Abstract Text</label>
            <textarea v-model="editModal.form.abstract_text" rows="10"
              class="w-full px-3 py-2.5 border border-gray-200 rounded-xl text-sm focus:outline-none focus:border-blue-400 focus:ring-1 focus:ring-blue-400 resize-y leading-relaxed font-[inherit]"></textarea>
          </div>

          <p class="text-xs text-gray-400 italic">
            To edit authors, open the
            <button @click="$router.push({ name: 'Abstract', params: { id: editModal.form.id } }); closeEditModal()"
              class="text-blue-500 hover:underline">full abstract view →</button>
          </p>
        </div>

        <!-- Modal footer -->
        <div class="flex justify-end gap-3 px-6 py-4 border-t border-gray-100 flex-shrink-0">
          <button @click="closeEditModal"
            class="px-5 py-2 rounded-xl text-sm font-semibold border border-gray-200 text-gray-600 hover:bg-gray-50 transition">
            Cancel
          </button>
          <button @click="saveEditModal" :disabled="editModal.saving"
            class="px-6 py-2 rounded-xl text-sm font-semibold text-white bg-blue-500 hover:bg-blue-600 transition disabled:opacity-50">
            {{ editModal.saving ? 'Saving…' : 'Save Changes' }}
          </button>
        </div>

      </div>
    </div>
  </Teleport>

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

// Registration filter values that require server-side filtering
const REGISTRATION_FILTERS = ['registered', 'not_registered', 'paid']

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
      abstractsPage: 1, abstractsPageSize: 25,
      abstractsTotal: 0, abstractsSearch: '',
      abstractsFilter: 'all',  // 'all' | 'oral' | 'poster' | 'presenters' | 'multi'
      abstractsSort: { field: 'created_at', dir: 'desc' },
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

      // ── Presenter registration status map (email → {has_registered, has_paid}) ──
      presenterStatusMap: {},
      presenterStatusLoading: false,

      // ── Edit modal ────────────────────────────────────────────────────────
      editModal: {
        open: false,
        saving: false,
        successMsg: '',
        errorMsg: '',
        form: {
          id: null,
          title: '',
          presentation_type: 'oral',
          status: 'accepted',
          track: '',
          keywords: '',
          abstract_text: '',
        },
      },
    }
  },

  computed: {
    abstractsTotalPages() { return Math.max(1, Math.ceil(this.abstractsTotal / this.abstractsPageSize)) },
    uploadsTotalPages()   { return Math.max(1, Math.ceil(this.uploadsTotal / this.uploadsPageSize)) },
    // Client-side sort for presenter (server sorts by title/type/date)
    sortedAbstracts() {
      if (this.abstractsSort.field !== 'presenter') return this.abstracts
      return [...this.abstracts].sort((a, b) => {
        const pa = this.presenterName(a).toLowerCase()
        const pb = this.presenterName(b).toLowerCase()
        const cmp = pa < pb ? -1 : pa > pb ? 1 : 0
        return this.abstractsSort.dir === 'asc' ? cmp : -cmp
      })
    },
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
    this.loadPresenterStatuses()
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
        if (this.abstractsFilter === 'oral')           params.presentation_type = 'oral'
        if (this.abstractsFilter === 'poster')         params.presentation_type = 'poster'
        if (this.abstractsFilter === 'multi')          params.presenter_email = 'multi'
        if (this.abstractsFilter === 'registered')     params.presenter_registered = 'yes'
        if (this.abstractsFilter === 'not_registered') params.presenter_registered = 'no'
        if (this.abstractsFilter === 'paid')           params.presenter_paid = 'yes'
        // presenter sort is handled client-side; all others are server-side
        if (this.abstractsSort.field !== 'presenter') {
          params.sort_by  = this.abstractsSort.field
          params.sort_dir = this.abstractsSort.dir
        }

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

    setSort(field) {
      if (this.abstractsSort.field === field) {
        this.abstractsSort.dir = this.abstractsSort.dir === 'asc' ? 'desc' : 'asc'
      } else {
        this.abstractsSort.field = field
        this.abstractsSort.dir = field === 'title' ? 'asc' : 'desc'
      }
      this.abstractsPage = 1
      // presenter sort is client-side only — no reload needed
      if (field !== 'presenter') this.loadAbstracts()
    },

    // ── Presenter registration status ─────────────────────────────────────
    async loadPresenterStatuses() {
      this.presenterStatusLoading = true
      try {
        const res = await axios.get(`${this.apiUrl}/abstracts/presenter-registration-status`, {
          headers: { Authorization: `Bearer ${this.accessToken}` },
        })
        this.presenterStatusMap = res.data || {}
      } catch (e) { console.error('presenter status:', e) }
      finally { this.presenterStatusLoading = false }
    },

    presenterStatus(abstract) {
      const email = this.presenterEmail(abstract)
      if (!email) return null
      return this.presenterStatusMap[email.toLowerCase()] || null
    },

    // ── Edit modal ────────────────────────────────────────────────────────
    openEditModal(abstract) {
      this.editModal.successMsg = ''
      this.editModal.errorMsg = ''
      this.editModal.saving = false
      this.editModal.form = {
        id: abstract.id,
        title: abstract.title || '',
        presentation_type: abstract.presentation_type || 'oral',
        status: abstract.status || 'accepted',
        track: abstract.track || '',
        keywords: abstract.keywords || '',
        abstract_text: abstract.abstract_text || '',
      }
      this.editModal.open = true
    },

    closeEditModal() {
      this.editModal.open = false
    },

    async saveEditModal() {
      this.editModal.saving = true
      this.editModal.successMsg = ''
      this.editModal.errorMsg = ''
      try {
        const f = this.editModal.form
        await axios.put(
          `${this.apiUrl}/abstracts/${f.id}`,
          {
            title: f.title.trim(),
            presentation_type: f.presentation_type,
            status: f.status,
            track: f.track.trim(),
            keywords: f.keywords.trim(),
            abstract_text: f.abstract_text.trim(),
          },
          { headers: { Authorization: `Bearer ${this.accessToken}` } }
        )
        // Update the abstract in the local list
        const idx = this.abstracts.findIndex(a => a.id === f.id)
        if (idx !== -1) {
          this.abstracts[idx] = {
            ...this.abstracts[idx],
            title: f.title,
            presentation_type: f.presentation_type,
            status: f.status,
            track: f.track,
            keywords: f.keywords,
            abstract_text: f.abstract_text,
          }
        }
        this.editModal.successMsg = 'Saved successfully.'
        setTimeout(() => { this.editModal.open = false }, 1200)
      } catch (e) {
        this.editModal.errorMsg = e.response?.data?.detail || 'Failed to save.'
      } finally {
        this.editModal.saving = false
      }
    },

    presenterName(abstract) {
      const authors = abstract.authors || []
      const presenter = authors.find(au => au.is_presenting) || authors[0]
      if (presenter) return [presenter.firstname, presenter.lastname].filter(Boolean).join(' ') || '—'
      return abstract.submitter_name || '—'
    },
    presenterEmail(abstract) {
      const authors = abstract.authors || []
      const presenter = authors.find(au => au.is_presenting) || null
      return presenter?.email || ''
    },

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
