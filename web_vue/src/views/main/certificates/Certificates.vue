<template>
  <div class="flex flex-col space-y-4 flex-1">
    <HeaderView :headerTitle="'Certificates'" />

    <!-- Event + certificate type -->
    <div class="bg-white border border-gray-100 rounded-xl shadow-sm p-5 space-y-4">
      <div>
        <label class="block text-xs font-bold uppercase tracking-widest text-gray-400 mb-1.5">Select Event</label>
        <select v-model="selectedEventId" @change="loadPeople"
          class="w-full border border-gray-200 rounded-xl px-3 py-2.5 text-sm text-gray-700 focus:outline-none bg-white">
          <option value="">— Choose an event —</option>
          <option v-for="event in events" :key="event.id" :value="event.id">{{ event.event }}</option>
        </select>
      </div>

      <div>
        <label class="block text-xs font-bold uppercase tracking-widest text-gray-400 mb-1.5">Certificate Type</label>
        <div class="flex flex-wrap items-center gap-2">
          <button v-for="(t, key) in types" :key="key" type="button" @click="setType(key)"
            class="px-4 py-2 rounded-xl text-xs font-semibold transition"
            :class="type === key ? 'text-white' : 'bg-gray-50 text-gray-600 hover:bg-gray-100'"
            :style="type === key ? { backgroundColor: 'rgb(254,80,103)' } : {}">
            {{ t.label }} <span class="opacity-80 ml-1">· {{ t.cpd }} CPD</span>
          </button>
          <button type="button" @click="preview"
            class="ml-auto inline-flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-semibold text-gray-600 bg-gray-50 hover:bg-gray-100 transition">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
            </svg>
            Preview Template
          </button>
        </div>
        <p class="text-xs text-gray-400 mt-2">{{ sourceHint }}</p>
      </div>
    </div>

    <!-- No event selected -->
    <div v-if="!selectedEventId" class="bg-white rounded-2xl shadow-sm py-20 flex flex-col items-center justify-center text-center px-6">
      <p class="text-gray-500 text-base font-medium mb-1">Select an event to generate certificates</p>
      <p class="text-gray-400 text-sm">Presenters (plenary, oral &amp; poster), ushers/secretariat, and other paid delegates are loaded from the event</p>
    </div>

    <!-- Spinner -->
    <div v-else-if="isLoading" class="flex justify-center py-12">
      <svg class="animate-spin h-8 w-8" style="color: rgb(254,80,103);" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
      </svg>
    </div>

    <template v-else>
      <div class="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
        <!-- Toolbar -->
        <div class="px-4 py-3 border-b border-gray-200 flex flex-wrap items-center gap-x-3 gap-y-2">
          <div class="relative">
            <svg class="w-3.5 h-3.5 absolute left-2.5 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none"
              fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-4.35-4.35M17 11a6 6 0 11-12 0 6 6 0 0112 0z"/>
            </svg>
            <input v-model="search" type="text" placeholder="Search name or email"
              class="w-56 pl-8 pr-3 py-1.5 text-[13px] border border-gray-200 rounded-md bg-white text-gray-700
                     placeholder:text-gray-400 focus:outline-none focus:border-brand focus:ring-2 focus:ring-brand/15" />
          </div>

          <label v-if="type === 'attendee'"
            class="inline-flex items-center gap-1.5 text-[12px] text-gray-500 font-medium select-none cursor-pointer">
            <input type="checkbox" v-model="attendedOnly" class="rounded border-gray-300 text-brand focus:ring-brand/30" />
            Scanned as attended
          </label>

          <div class="flex flex-wrap items-center gap-1.5">
            <button type="button" @click="emailOnly = !emailOnly" :aria-pressed="emailOnly"
              class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-[12px] font-medium border transition"
              :class="emailOnly
                ? 'text-white border-transparent'
                : 'text-gray-500 border-gray-200 bg-white hover:border-gray-300 hover:text-gray-700'"
              :style="emailOnly ? { backgroundColor: 'rgb(254,80,103)' } : {}">
              <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/>
              </svg>
              Has email
              <span class="tabular-nums opacity-70">{{ withEmailCount }}</span>
            </button>

            <button type="button" @click="paidFilter = paidFilter === 'paid' ? '' : 'paid'" :aria-pressed="paidFilter === 'paid'"
              class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-[12px] font-medium border transition"
              :class="paidFilter === 'paid'
                ? 'text-white border-transparent'
                : 'text-gray-500 border-gray-200 bg-white hover:border-gray-300 hover:text-gray-700'"
              :style="paidFilter === 'paid' ? { backgroundColor: 'rgb(16,185,129)' } : {}">
              <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/>
              </svg>
              Paid
              <span class="tabular-nums opacity-70">{{ paidCount }}</span>
            </button>

            <button type="button" @click="paidFilter = paidFilter === 'unpaid' ? '' : 'unpaid'" :aria-pressed="paidFilter === 'unpaid'"
              class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-[12px] font-medium border transition"
              :class="paidFilter === 'unpaid'
                ? 'text-white border-transparent'
                : 'text-gray-500 border-gray-200 bg-white hover:border-gray-300 hover:text-gray-700'"
              :style="paidFilter === 'unpaid' ? { backgroundColor: 'rgb(245,158,11)' } : {}">
              <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z"/>
              </svg>
              Unpaid
              <span class="tabular-nums opacity-70">{{ unpaidCount }}</span>
            </button>

            <!-- Email status (from GET /certificates/sent). "Not sent" is the
                 resend list: failed + never attempted. -->
            <button type="button" @click="sentFilter = sentFilter === 'unsent' ? '' : 'unsent'" :aria-pressed="sentFilter === 'unsent'"
              class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-[12px] font-medium border transition"
              :class="sentFilter === 'unsent'
                ? 'text-white border-transparent'
                : 'text-gray-500 border-gray-200 bg-white hover:border-gray-300 hover:text-gray-700'"
              :style="sentFilter === 'unsent' ? { backgroundColor: 'rgb(220,50,75)' } : {}">
              <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M21.75 6.75v10.5a2.25 2.25 0 01-2.25 2.25h-15a2.25 2.25 0 01-2.25-2.25V6.75m19.5 0A2.25 2.25 0 0019.5 4.5h-15a2.25 2.25 0 00-2.25 2.25m19.5 0l-9.75 6.75L2.25 6.75"/>
              </svg>
              Not sent
              <span class="tabular-nums opacity-70">{{ notSentCount }}</span>
            </button>

            <button type="button" @click="sentFilter = sentFilter === 'sent' ? '' : 'sent'" :aria-pressed="sentFilter === 'sent'"
              class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-[12px] font-medium border transition"
              :class="sentFilter === 'sent'
                ? 'text-white border-transparent'
                : 'text-gray-500 border-gray-200 bg-white hover:border-gray-300 hover:text-gray-700'"
              :style="sentFilter === 'sent' ? { backgroundColor: 'rgb(71,85,105)' } : {}">
              <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/>
              </svg>
              Sent
              <span class="tabular-nums opacity-70">{{ sentCount }}</span>
            </button>

            <template v-if="type === 'attendee'">
              <button v-for="c in attendeeCategories" :key="c.name" type="button" @click="toggleAttendeeCategory(c.name)"
                :aria-pressed="attendeeCategoryFilter.includes(c.name)"
                class="px-2.5 py-1 rounded-md text-[12px] font-medium border transition capitalize"
                :class="attendeeCategoryFilter.includes(c.name)
                  ? 'text-white border-transparent'
                  : 'text-gray-500 border-gray-200 bg-white hover:border-gray-300 hover:text-gray-700'"
                :style="attendeeCategoryFilter.includes(c.name) ? { backgroundColor: 'rgb(254,80,103)' } : {}">
                {{ c.name }} <span class="tabular-nums opacity-70">{{ c.count }}</span>
              </button>
            </template>

            <template v-if="type === 'presenter'">
              <button v-for="c in presenterCategories" :key="c.name" type="button" @click="toggleCategory(c.name)"
                :aria-pressed="categoryFilter.includes(c.name)"
                class="px-2.5 py-1 rounded-md text-[12px] font-medium border transition capitalize"
                :class="categoryFilter.includes(c.name)
                  ? 'text-white border-transparent'
                  : 'text-gray-500 border-gray-200 bg-white hover:border-gray-300 hover:text-gray-700'"
                :style="categoryFilter.includes(c.name) ? { backgroundColor: 'rgb(254,80,103)' } : {}">
                {{ presenterCategoryLabel(c.name) }}
                <span class="tabular-nums opacity-70">{{ c.count }}</span>
              </button>
            </template>
          </div>

          <div class="ml-auto flex items-baseline gap-1.5 text-[12px] tabular-nums">
            <span class="text-gray-400">{{ filteredPeople.length }} shown</span>
            <span v-if="selectedCount" class="text-gray-900 font-semibold">· {{ selectedCount }} selected</span>
          </div>
        </div>

        <div class="overflow-x-auto max-h-[60vh] overflow-y-auto">
          <table class="w-full min-w-[760px] text-[13px]">
            <thead class="sticky top-0 z-10">
              <tr class="bg-white text-[11px] font-semibold uppercase tracking-[0.07em] text-gray-400 border-b border-gray-200">
                <th class="pl-4 pr-2 py-2.5 text-left w-9">
                  <input type="checkbox" :checked="allShownSelected" @change="toggleAllShown($event.target.checked)"
                    class="rounded border-gray-300 text-brand focus:ring-brand/30" title="Select all shown" />
                </th>
                <th class="px-2 py-2.5 text-left w-10" title="Row number">#</th>
                <th class="px-2 py-2.5 text-left">Name on certificate</th>
                <th v-if="type !== 'presenter'" class="px-2 py-2.5 text-left">Email</th>
                <th v-if="type !== 'presenter'" class="px-2 py-2.5 text-left whitespace-nowrap">Category</th>
                <th class="px-2 py-2.5 text-left">{{ type === 'presenter' ? 'Presentation' : 'Country' }}</th>
                <th class="pl-2 pr-4 py-2.5 text-right whitespace-nowrap">Action</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100">
              <tr v-for="(p, idx) in filteredPeople" :key="p.key"
                class="group transition-colors hover:bg-brand/[0.035]"
                :class="selected[p.key] ? 'bg-brand/[0.05] shadow-[inset_2px_0_0_rgb(254,80,103)]' : ''">
                <td class="pl-4 pr-2 py-2">
                  <input type="checkbox" :checked="!!selected[p.key]" @change="toggle(p.key, $event.target.checked)"
                    class="rounded border-gray-300 text-brand focus:ring-brand/30" />
                </td>
                <td class="px-2 py-2 text-[11.5px] text-gray-300 tabular-nums">{{ idx + 1 }}</td>
                <td class="px-2 py-2 font-medium text-gray-900">
                  <div class="whitespace-nowrap flex items-center gap-1.5">
                    <span v-if="p.paid !== undefined"
                      class="inline-flex items-center rounded px-1.5 py-0.5 text-[9.5px] font-bold uppercase tracking-wide leading-none"
                      :class="p.paid
                        ? 'bg-green-100 text-green-700'
                        : 'bg-amber-100 text-amber-700'"
                      :title="p.paid ? 'Registration paid' : 'Registration not paid'">
                      {{ p.paid ? 'Paid' : 'Unpaid' }}
                    </span>
                    <span class="truncate">{{ p.name }}</span>
                  </div>
                  <!-- Presenters have no Email column (the table gets wide), so the
                       address sits under the name instead. -->
                  <a v-if="type === 'presenter' && p.email" :href="`mailto:${p.email}`"
                    class="mt-0.5 block text-[12px] font-normal text-gray-500 hover:text-brand transition-colors break-all">
                    {{ p.email }}
                  </a>
                  <span v-else-if="type === 'presenter'" class="mt-0.5 block text-[12px] font-normal text-gray-300">—</span>
                </td>
                <td v-if="type !== 'presenter'" class="px-2 py-2">
                  <a v-if="p.email" :href="`mailto:${p.email}`"
                    class="text-[12.5px] text-gray-500 hover:text-brand transition-colors break-all">
                    {{ p.email }}
                  </a>
                  <span v-else class="text-[12.5px] text-gray-300">—</span>
                </td>
                <td v-if="type !== 'presenter'" class="px-2 py-2 whitespace-nowrap">
                  <span class="inline-flex items-center rounded-full border border-gray-200 bg-gray-50 px-2 py-0.5 text-[11px] font-medium text-gray-600">
                    {{ p.category }}
                  </span>
                </td>
                <td class="px-2 py-2 text-[12.5px] text-gray-500">
                  <!-- Falls back to the session/category text when a presenter has
                       no presentation title (e.g. abstract-only, no programme slot). -->
                  <span v-if="p.detail || p.category">{{ p.detail || p.category }}</span>
                  <span v-else class="text-gray-300">—</span>
                </td>
                <td class="pl-2 pr-4 py-2 text-right whitespace-nowrap">
                  <button v-if="p.sent" type="button" @click="openEmailModal([p])" :disabled="!!emailModal"
                    class="inline-flex items-center gap-1 rounded-full bg-green-50 border border-green-200 text-green-700 px-2 py-0.5 text-[10px] font-bold uppercase tracking-wide mr-1.5
                           hover:border-green-300 hover:bg-green-100 disabled:opacity-50 disabled:cursor-not-allowed"
                    title="Certificate already sent to this address — click to preview it">
                    <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/>
                    </svg>
                    Sent
                  </button>
                  <button v-if="p.email" type="button" @click="openEmailModal([p])"
                    :disabled="!!emailModal"
                    class="inline-flex items-center gap-1.5 rounded-md border px-2.5 py-1 text-[12px] font-semibold transition
                           disabled:opacity-40 disabled:cursor-not-allowed"
                    :class="rowMsg && rowMsg.key === p.key
                      ? (rowMsg.ok
                          ? 'border-green-200 bg-green-50 text-green-700'
                          : 'border-red-200 bg-red-50 text-red-600')
                      : (p.sent
                          ? 'border-amber-300 bg-amber-50 text-amber-700 hover:border-amber-400'
                          : 'border-gray-200 bg-white text-gray-600 hover:border-brand/50 hover:text-brand hover:bg-brand/5')">
                    <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
                    </svg>
                    {{ rowMsg && rowMsg.key === p.key ? rowMsg.text : (p.sent ? 'Resend' : 'Preview & Send') }}
                  </button>
                  <span v-else class="text-[12px] text-gray-300 italic">Not emailable</span>
                </td>
              </tr>
            </tbody>
          </table>
          <div v-if="filteredPeople.length === 0" class="py-16 text-center">
            <p class="text-gray-400 text-sm">No one matches the current filters</p>
            <p class="text-gray-300 text-xs mt-1">Clear the filters above, or type names under "Additional names" below</p>
          </div>
        </div>
      </div>

      <!-- Extra names + generate -->
      <div class="bg-white rounded-2xl shadow-sm p-5 space-y-3">
        <div>
          <label class="block text-xs font-bold uppercase tracking-widest text-gray-400 mb-1.5">Additional names</label>
          <textarea v-model="extraNames" rows="4"
            placeholder="Anyone not in the list above — one full name per line, exactly as it should appear"
            class="w-full border border-gray-200 rounded-xl px-3 py-2 text-sm focus:outline-none"></textarea>
        </div>
        <div v-if="emailSuccess" class="p-3 rounded-xl text-sm text-green-700 bg-green-50 border border-green-200">{{ emailSuccess }}</div>

        <div class="flex flex-wrap items-center gap-3">
          <p class="text-xs text-gray-400 flex-1">
            <strong>Generate</strong> opens a print tab — choose <strong>Save as PDF</strong> and turn on
            <strong>Background graphics</strong> for one PDF with a page per person.
            <strong>Email</strong> opens a preview you can edit before sending — each selected person gets their own
            certificate as a PDF at their registration email, followed by the event's public Links (Links tab);
            people typed under "Additional names" have no email on file and are skipped. ALL-CAPS / lowercase names
            are tidied to Title Case.
          </p>
          <button type="button" @click="openEmailModal(emailableSelected)" :disabled="!emailableSelected.length || !!emailModal"
            class="inline-flex items-center gap-1.5 px-5 py-2.5 rounded-xl text-sm font-semibold border-2 transition disabled:opacity-40"
            style="border-color: rgb(254,80,103); color: rgb(254,80,103);">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
            </svg>
            Email {{ emailableSelected.length }} Certificate{{ emailableSelected.length === 1 ? '' : 's' }}
          </button>
          <button type="button" @click="generate" :disabled="!finalNames.length"
            class="inline-flex items-center gap-1.5 px-5 py-2.5 rounded-xl text-sm font-semibold text-white transition hover:opacity-90 disabled:opacity-40"
            style="background-color: rgb(254,80,103);">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
            </svg>
            Generate {{ finalNames.length }} Certificate{{ finalNames.length === 1 ? '' : 's' }}
          </button>
        </div>
        <p v-if="skippedNoEmailCount" class="text-[11px] text-gray-400">
          {{ skippedNoEmailCount }} selected {{ skippedNoEmailCount === 1 ? 'person has' : 'people have' }} no email on file and will be skipped by Email (still included in Generate).
        </p>
      </div>

      <!-- Certificates of Appreciation — individual officials, sent one at a
           time with their own CC list (utils/certificateTypes.js). -->
      <div class="bg-white rounded-2xl shadow-sm p-5">
        <div class="flex items-start justify-between gap-3">
          <div>
            <div class="text-xs font-bold uppercase tracking-widest text-gray-400">Certificates of Appreciation</div>
            <p class="text-xs text-gray-400 mt-1">For officials who supported the College in hosting the event. Each is previewed and sent individually, with the CC list shown before sending.</p>
          </div>
        </div>
        <div class="mt-3 divide-y divide-gray-100 border border-gray-100 rounded-xl">
          <div v-for="r in appreciationRecipients" :key="r.key" class="flex flex-wrap items-center gap-3 px-4 py-3">
            <div class="flex-1 min-w-[220px]">
              <div class="text-sm font-semibold text-gray-800">{{ r.name }}</div>
              <div class="text-xs text-gray-500">{{ r.designation }}</div>
              <div class="text-xs text-gray-400 mt-0.5">
                {{ r.email }}<span v-if="r.cc.length"> · CC {{ r.cc.join(', ') }}</span>
              </div>
            </div>
            <span v-if="sentEmails.has(r.email.toLowerCase())"
              class="px-2 py-0.5 rounded-full text-[11px] font-semibold bg-green-50 text-green-700">Sent</span>
            <button type="button" @click="openAppreciationModal(r)" :disabled="!!emailModal"
              class="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl text-sm font-semibold text-white transition hover:opacity-90 disabled:opacity-40"
              style="background-color: rgb(254,80,103);">
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
              </svg>
              {{ sentEmails.has(r.email.toLowerCase()) ? 'Preview & Resend' : 'Preview & Send' }}
            </button>
          </div>
        </div>
      </div>

      <!-- Certificates of Appreciation for the drivers — no emails, so these
           are only generated/downloaded (never emailed). -->
      <div class="bg-white rounded-2xl shadow-sm p-5">
        <div class="flex items-start justify-between gap-3">
          <div>
            <div class="text-xs font-bold uppercase tracking-widest text-gray-400">Certificates of Appreciation — Drivers</div>
            <p class="text-xs text-gray-400 mt-1">Ministry of Health Zanzibar drivers and driver-officers. No emails on file, so these are generated/downloaded as one PDF (a page per person), not emailed.</p>
          </div>
        </div>
        <div class="mt-3 divide-y divide-gray-100 border border-gray-100 rounded-xl">
          <div v-for="g in appreciationDriverGroups" :key="g.key" class="px-4 py-3">
            <div class="text-sm font-semibold text-gray-800">{{ g.designation }}</div>
            <div class="mt-1.5 flex flex-wrap gap-1.5">
              <span v-for="n in g.names" :key="n"
                class="inline-flex items-center rounded-full border border-gray-200 bg-gray-50 px-2.5 py-1 text-[12px] text-gray-700">
                {{ n }}
              </span>
            </div>
          </div>
        </div>
        <div class="mt-3">
          <button type="button" @click="generateDrivers"
            class="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl text-sm font-semibold text-white transition hover:opacity-90"
            style="background-color: rgb(254,80,103);">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
            </svg>
            Generate {{ driverCount }} Certificates of Appreciation
          </button>
        </div>
      </div>
    </template>

    <!-- Preview & edit email modal (both per-row Send and bulk Email open this) -->
    <div v-if="emailModal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50" @click.self="closeEmailModal">
      <div class="relative w-full max-w-2xl">
      <div class="bg-white rounded-2xl shadow-xl w-full max-h-[90vh] overflow-y-auto">
        <div class="px-5 py-4 border-b border-gray-100 flex items-center justify-between sticky top-0 bg-white z-10">
          <div>
            <div class="font-bold text-gray-800">{{ emailModal.appreciation ? 'Preview &amp; Send Certificate of Appreciation' : 'Preview &amp; Edit Certificate Email' }}</div>
            <p class="text-xs text-gray-500 mt-0.5">
              {{ emailModal.recipients.length === 1 ? `To ${emailModal.recipients[0].email}` : `${emailModal.recipients.length} recipients` }}
              — use <code class="bg-gray-100 px-1 rounded">{{ mergeTagExample }}</code> and <code class="bg-gray-100 px-1 rounded">{{ mergeTagEventExample }}</code> in Subject/Message to personalize each one.
            </p>
          </div>
          <button type="button" @click="closeEmailModal" :disabled="emailModal.sending" class="text-gray-400 hover:text-gray-600 flex-shrink-0 ml-3 disabled:opacity-40">
            <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" d="M6 18L18 6M6 6l12 12"/></svg>
          </button>
        </div>

        <div class="p-5 space-y-4">
          <div v-if="emailModal.recipients.length > 1">
            <label class="block text-xs font-bold uppercase tracking-widest text-gray-400 mb-1.5">Previewing as</label>
            <select v-model="emailModal.previewKey" @change="refreshPreview"
              class="w-full border border-gray-200 rounded-xl px-3 py-2 text-sm focus:outline-none bg-white">
              <option v-for="p in emailModal.recipients" :key="p.key" :value="p.key">{{ p.name }} — {{ p.email }}</option>
            </select>
          </div>

          <div v-if="emailModal.appreciation">
            <label class="block text-xs font-bold uppercase tracking-widest text-gray-400 mb-1.5">CC</label>
            <input v-model="emailModal.cc" type="text" placeholder="name@example.org, other@example.org"
              class="w-full border border-gray-200 rounded-xl px-3 py-2 text-sm focus:outline-none" />
            <p class="text-[11px] text-gray-400 mt-1">Separate addresses with commas. Leave blank for no CC.</p>
          </div>

          <div v-if="emailModal.appreciation">
            <label class="block text-xs font-bold uppercase tracking-widest text-gray-400 mb-1.5">Attach a letter (PDF, optional)</label>
            <div v-if="emailModal.letterFile" class="flex items-center gap-3 rounded-xl border border-gray-200 px-3 py-2">
              <svg class="w-5 h-5 flex-shrink-0" style="color: rgb(220,50,75);" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z"/>
              </svg>
              <div class="flex-1 min-w-0">
                <div class="text-sm text-gray-800 truncate">{{ emailModal.letterFile.name }}</div>
                <div class="text-[11px] text-gray-400">{{ Math.max(1, Math.round(emailModal.letterFile.size / 1024)) }} KB</div>
              </div>
              <button type="button" @click="clearLetter" :disabled="emailModal.sending" class="text-xs font-semibold text-gray-500 hover:text-gray-800">Remove</button>
            </div>
            <label v-else class="flex items-center justify-center gap-2 rounded-xl border border-dashed border-gray-300 px-3 py-3 text-sm text-gray-500 cursor-pointer hover:border-gray-400">
              <input type="file" accept="application/pdf,.pdf" class="hidden" @change="onLetterPicked" />
              Choose a PDF letter to send with the certificate
            </label>
            <p v-if="emailModal.letterError" class="text-[11px] text-red-600 mt-1">{{ emailModal.letterError }}</p>
          </div>

          <div>
            <label class="block text-xs font-bold uppercase tracking-widest text-gray-400 mb-1.5">Subject</label>
            <input v-model="emailModal.subject" type="text"
              class="w-full border border-gray-200 rounded-xl px-3 py-2 text-sm focus:outline-none" />
          </div>
          <div>
            <label class="block text-xs font-bold uppercase tracking-widest text-gray-400 mb-1.5">Message (shown above the certificate)</label>
            <textarea v-model="emailModal.message" rows="5"
              class="w-full border border-gray-200 rounded-xl px-3 py-2 text-sm focus:outline-none"></textarea>
            <p class="text-[11px] text-gray-400 mt-1">Leave blank to send just the certificate, no message text.</p>
          </div>

<!-- Live preview — the real certificate sheet, scaled exactly
                   like the print page (#/certificates/print), so what you see
                   here is structurally identical to what gets printed/emailed. -->
              <div class="rounded-xl border border-gray-200 overflow-hidden">
                <div class="px-4 py-2 bg-gray-50 border-b border-gray-100 text-xs font-semibold text-gray-500 uppercase tracking-wide">Email preview</div>
                <div class="p-4 space-y-3 bg-white">
                  <div class="text-sm"><span class="text-gray-400">Subject: </span><span class="font-semibold text-gray-800">{{ resolvedPreview.subject }}</span></div>
                  <div v-if="resolvedPreview.message" class="text-sm text-gray-700 whitespace-pre-line">{{ resolvedPreview.message }}</div>
                  <div class="flex justify-center py-4 bg-gray-100 rounded-lg overflow-hidden">
                    <div v-if="emailModal.rendering" class="py-10"><SpinnerComponent /></div>
                    <div v-else class="cert-preview-scaled" :style="previewScaleStyle">
                      <CertificateSheet ref="previewSheet" :name="previewName" :type="modalCertType" :designation="previewDesignation"
                        :event-name="selectedEventName" uid="email-preview" />
                    </div>
                  </div>
                  <p class="text-[11px] text-gray-400">
                    Delivered as a PDF attachment (rendered above as the live certificate) — most inboxes will also display this image directly in the message.
                  </p>
              <!-- Mirrors mailer_util.links_to_html() — keep the two in step. -->
              <div v-if="emailModal.appreciation" class="pt-3 border-t border-gray-100 text-xs text-gray-500">
                <span class="font-semibold text-gray-600">Attachments:</span>
                Certificate of Appreciation – {{ previewName }}.pdf<span v-if="emailModal.letterFile">, {{ emailModal.letterFile.name }}</span>
                <div class="text-[11px] text-gray-400 mt-0.5">No conference links are added to appreciation emails.</div>
              </div>
              <div v-else-if="eventLinks.length" class="pt-3 border-t border-gray-100">
                <div class="text-xs font-bold uppercase mb-2.5" style="letter-spacing: 1.5px; color: rgb(220,50,75);">Useful links</div>
                <div class="space-y-2.5">
                  <div v-for="l in eventLinks" :key="l.id"
                    class="flex items-center gap-3 bg-white rounded-[10px] px-3.5 py-3"
                    style="border: 1px solid #f3d3d9; border-left: 4px solid #fe5066;">
                    <div class="w-9 h-9 flex-shrink-0 rounded-lg flex items-center justify-center text-lg" style="background: #fff0f2;">{{ linkIcon(l.name) }}</div>
                    <div class="flex-1 min-w-0">
                      <a :href="l.link" target="_blank" class="block text-[15px] font-bold text-gray-800 truncate hover:underline">{{ l.name }}</a>
                      <div class="text-xs text-gray-500 truncate">{{ linkHost(l.link) }}</div>
                    </div>
                    <a :href="l.link" target="_blank"
                      class="flex-shrink-0 text-white text-[13px] font-bold px-3.5 py-2 rounded-md hover:opacity-90"
                      style="background: #fe5066;">Open &rarr;</a>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div v-if="emailModal.error" class="p-3 rounded-xl text-sm text-red-700 bg-red-50 border border-red-200">{{ emailModal.error }}</div>
        </div>

        <div class="px-5 py-4 border-t border-gray-100 flex justify-end gap-2 sticky bottom-0 bg-white">
          <button type="button" @click="closeEmailModal" :disabled="emailModal.sending" class="px-4 py-2 text-sm font-medium text-gray-600 hover:bg-gray-50 rounded-lg disabled:opacity-40">Cancel</button>
          <button type="button" @click="confirmSendEmail" :disabled="emailModal.sending || emailModal.rendering"
            class="inline-flex items-center gap-2 px-4 py-2 text-sm font-semibold text-white rounded-lg disabled:opacity-60"
            style="background-color: rgb(254,80,103);">
            <svg v-if="emailModal.sending" class="w-4 h-4 animate-spin" viewBox="0 0 24 24" fill="none">
              <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-opacity="0.3" stroke-width="3"/>
              <path d="M22 12a10 10 0 0 0-10-10" stroke="currentColor" stroke-width="3" stroke-linecap="round"/>
            </svg>
            {{ emailModal.sending
              ? (emailModal.recipients.length > 1 ? `Sending ${emailModal.progressDone}/${emailModal.progressTotal}…` : 'Sending…')
              : (emailModal.recipients.length > 1 ? `Send ${emailModal.recipients.length} Emails` : 'Send Email') }}
          </button>
        </div>
      </div>

      <!-- Dispatch progress — covers the card (not just its scrolled viewport)
           while certificates are rendered and uploaded. -->
      <div v-if="emailModal.sending"
        class="absolute inset-0 z-20 rounded-2xl bg-white/95 flex flex-col items-center justify-center px-8 text-center">
        <div class="relative w-32 h-32">
          <svg class="w-32 h-32 -rotate-90" viewBox="0 0 120 120" :class="{ 'animate-spin': !sendProgress.determinate }">
            <circle cx="60" cy="60" r="52" fill="none" stroke="#fde2e6" stroke-width="10"/>
            <circle cx="60" cy="60" r="52" fill="none" stroke="rgb(254,80,103)" stroke-width="10" stroke-linecap="round"
              :stroke-dasharray="sendProgress.circumference"
              :stroke-dashoffset="sendProgress.dashOffset"
              style="transition: stroke-dashoffset 0.4s ease;"/>
          </svg>
          <div class="absolute inset-0 flex flex-col items-center justify-center">
            <template v-if="sendProgress.determinate">
              <span class="text-2xl font-bold text-gray-800">{{ sendProgress.percent }}%</span>
              <span class="text-[11px] text-gray-500">{{ emailModal.progressDone }} / {{ emailModal.progressTotal }}</span>
            </template>
            <svg v-else class="w-8 h-8" style="color: rgb(254,80,103);" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8">
              <path stroke-linecap="round" stroke-linejoin="round" d="M21.75 6.75v10.5a2.25 2.25 0 01-2.25 2.25h-15a2.25 2.25 0 01-2.25-2.25V6.75m19.5 0A2.25 2.25 0 0019.5 4.5h-15a2.25 2.25 0 00-2.25 2.25m19.5 0v.243a2.25 2.25 0 01-1.07 1.916l-7.5 4.615a2.25 2.25 0 01-2.36 0L3.32 8.91a2.25 2.25 0 01-1.07-1.916V6.75"/>
            </svg>
          </div>
        </div>
        <div class="mt-5 font-bold text-gray-800">{{ emailModal.stage || 'Sending…' }}</div>
        <div v-if="emailModal.currentName" class="mt-1 text-sm text-gray-500 truncate max-w-full">{{ emailModal.currentName }}</div>
        <div v-if="sendProgress.determinate" class="mt-4 w-full max-w-xs h-1.5 bg-gray-100 rounded-full overflow-hidden">
          <div class="h-full rounded-full" style="background: rgb(254,80,103); transition: width 0.4s ease;" :style="{ width: sendProgress.percent + '%' }"></div>
        </div>
        <p class="mt-4 text-xs text-gray-400">Please keep this tab open until sending finishes.</p>
      </div>
      </div>
    </div>

    <!-- Off-screen certificate used to render each recipient's image before
    upload (Send/Email) — parked far off-window so it's never visible. -->
    <div style="position: fixed; left: -99999px; top: 0; pointer-events: none;" aria-hidden="true">
      <CertificateSheet ref="renderSheet" :name="renderJob.name" :type="renderJob.type" :designation="renderJob.designation"
        :event-name="selectedEventName" uid="email-render" />
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import HeaderView from '@/includes/Header.vue'
import CertificateSheet from '@/components/CertificateSheet.vue'
import SpinnerComponent from '@/components/Spinner.vue'
import { fetchData } from '@/services/apiService'
import { useAuthStore } from '@/store/authStore'
import { CERTIFICATE_TYPES, CERTIFICATE_JOB_KEY, APPRECIATION_TYPE, APPRECIATION_RECIPIENTS, APPRECIATION_DRIVER_GROUPS, DEFAULT_EVENT_NAME, certificateCategory, tidyName, ensureCertificateFonts } from '@/utils/certificateTypes'

const API_URL = import.meta.env.VITE_API_URL
// A paid abstract presenter who doesn't appear anywhere in the programme book.
// They still count as a presenter (that's how the event page pairs "Abstract
// Presenters" with "Paid"), so they get their own filter chip rather than
// being folded into a session type they don't have.
const ABSTRACT_ONLY_CATEGORY = 'abstract only'
const ABSTRACT_ONLY_LABEL = 'Abstract presenter — no programme slot'
// Certificate images are rendered client-side (same markup as the print
// page) then uploaded — batch emailing hands them to the server a handful
// at a time rather than one giant request.
const EMAIL_BATCH_SIZE = 15
const DEFAULT_EMAIL_SUBJECT = 'Your Certificate of Participation — {{name}}'

// Defaults for the Certificate of Appreciation dialog (editable before sending).
const APPRECIATION_EMAIL_SUBJECT = 'Certificate of Appreciation — {{name}}'
// Swapped in automatically when a letter is attached (and back when removed),
// unless the admin has already edited the message.
const APPRECIATION_EMAIL_MESSAGE_LETTER = [
  'Dear {{name}},',
  '',
  'On behalf of the East, Central and Southern Africa College of Nursing and Midwifery (ECSACONM), please find attached our letter of appreciation, together with a Certificate of Appreciation in recognition of your dedication and invaluable support to the College in hosting the {{event}} in Zanzibar.',
  '',
  'Your support contributed greatly to the success of the conference, and we are sincerely grateful.',
  '',
  'Warm regards,',
  'ECSACONM Secretariat',
].join('\n')
const APPRECIATION_EMAIL_MESSAGE = [
  'Dear {{name}},',
  '',
  'On behalf of the East, Central and Southern Africa College of Nursing and Midwifery (ECSACONM), please find attached a Certificate of Appreciation in recognition of your dedication and invaluable support to the College in hosting the {{event}} in Zanzibar.',
  '',
  'Your support contributed greatly to the success of the conference, and we are sincerely grateful.',
  '',
  'Warm regards,',
  'ECSACONM Secretariat',
].join('\n')
const DEFAULT_EMAIL_MESSAGE = [
  'Dear {{name}},',
  '',
  'Please find attached a copy of your certificate for your successful participation in the {{event}}.',
  '',
  'We have also included links below to the event photos, as well as the shared presentations from both the plenary and breakout-room (abstract) sessions.',
  '',
  'To view the conference programme and find your abstract or presentation, click the link Conference presentations below.',
  '',
  'From there you can:',
  '  ❖ Browse by day, room and category (Abstracts / Plenary) using the tabs at the top',
  '  ❖ Search by presenter name, title or abstract code using the search box',
  '  ❖ Preview or download the slides (with a preview available for most uploads)',
  '',
  'An online copy of the Conference Abstract Book is also available in your portal. Log in at https://events.ecsaconm.org, go to My Account → My Abstracts, and click View Abstract Book to preview or download it.',
  '',
  'If you do not see your abstract listed under the sessions, or your presentation is unavailable, kindly share it with us at admission@cosecsa.org or info@ecsaconm.org so we can add it and make it available to other delegates for wider dissemination.',
  '',
  'Warm regards,',
  'ECSACONM Secretariat',
].join('\n')

export default {
  name: 'CertificatesView',
  components: { HeaderView, CertificateSheet, SpinnerComponent },
  setup() {
    const authStore = useAuthStore()
    return { authStore }
  },
  data() {
    return {
      types: CERTIFICATE_TYPES,
      type: 'attendee',
      events: [],
      selectedEventId: '',
      isLoading: false,
      registrations: [],
      attendedRegIds: new Set(),
      programme: [],
      // Emails that already received a certificate (from GET /certificates/sent)
      // — drives the "Sent" label and the Resend action on each row.
      sentEmails: new Set(),
      // Public Links (event page's Links tab) — appended to every
      // certificate email as a "Useful links" block.
      eventLinks: [],
      search: '',
      // '' | 'sent' | 'unsent' — the Sent / Not sent chips.
      sentFilter: '',
      attendedOnly: false,
      categoryFilter: [],
      attendeeCategoryFilter: [],
      // Narrows the table to people who actually have an email on file — the
      // ones Email can act on. Applies to every tab.
      emailOnly: false,
      // Payment-status filter: '' (everyone), 'paid', or 'unpaid'.
      paidFilter: '',
      // person key -> true; kept per type so switching tabs doesn't lose ticks
      selections: { attendee: {}, presenter: {}, usher: {} },
      extraNames: '',
      // off-screen certificate used to rasterize each recipient's image
      // before upload — see renderCertificateImage()
      renderJob: { name: '', type: CERTIFICATE_TYPES.attendee, designation: '' },
      appreciationRecipients: APPRECIATION_RECIPIENTS,
      rowMsg: null,
      emailSuccess: '',
      // Preview & edit modal — opened by both the per-row Send button and
      // the bulk Email button (see openEmailModal()). null when closed.
      emailModal: null,
      // Referenced in the modal hint text — kept out of the template
      // literal because Vue's mustache parser can't handle a nested {{ }}
      // inside an interpolation.
      mergeTagExample: '{{name}}',
      mergeTagEventExample: '{{event}}',
    }
  },
  computed: {
    // Ring/bar state for the dispatch overlay. Bulk sends show real progress
    // (certificates prepared / total); a single send just spins.
    sendProgress() {
      const m = this.emailModal
      const circumference = 2 * Math.PI * 52
      const determinate = !!m && m.progressTotal > 1
      const pct = determinate ? Math.round((m.progressDone / m.progressTotal) * 100) : 25
      return {
        determinate,
        percent: pct,
        circumference,
        dashOffset: circumference * (1 - pct / 100),
      }
    },
    selected() {
      return this.selections[this.type]
    },
    sourceHint() {
      return {
        attendee: 'Other paid delegates — registered, paid (secretariat always counts as paid), and not a presenter, usher or secretariat member. Member State, Other Africa, Participant and Exhibitor registrations are all grouped as one "Delegate" category. Use the category buttons to narrow the list; tick "only scanned as attended" to limit it to people whose QR badge was scanned.',
        presenter: 'Everyone named in the conference programme (Presentations by Room and the plenary schedule) plus every paid abstract presenter, one row per person, cross-matched to their registration for an email.',
        usher: 'Ushers, secretariat/support staff and the media team — registered with either role, same certificate for all three. Media keep their own "Media" label.',
      }[this.type]
    },
    // Lookup sets used to keep a presenter out of the delegate list, so they
    // never get mailed two certificates. Email is the reliable join (a
    // programme slot is matched to a registration server-side); the name set
    // is the fallback for presenters with no email on file.
    presenterEmails() {
      return new Set(this.presenters.map(p => (p.email || '').trim().toLowerCase()).filter(Boolean))
    },
    presenterNames() {
      return new Set(this.presenters.map(p => p.name.toLowerCase()))
    },
    people() {
      if (this.type === 'presenter') return this.presenters
      // A presenter shouldn't also show up (and get double-emailed) under
      // "other delegates" just because they also have a paid registration.
      const regs = this.registrations.filter(r => {
        const isSupport = this.isSupportRole(r)
        if (this.type === 'usher') return isSupport
        if (isSupport || !r.paid) return false
        if (this.isPresenter(r)) return false
        const cats = this.attendeeCategoryFilter
        if (cats.length && !cats.includes(this.roleLabel(r))) return false
        return !this.attendedOnly || this.attendedRegIds.has(r.id)
      })
      return regs.map(r => ({
        key: `reg-${r.id}`,
        name: tidyName([r.title, r.firstname, r.lastname].filter(Boolean).join(' ')),
        category: this.roleLabel(r),
        detail: r.country || '',
        email: r.email || '',
        paid: !!r.paid,
        sent: this.sentEmails.has((r.email || '').trim().toLowerCase()),
      })).sort((a, b) => a.name.localeCompare(b.name))
    },
    presenters() {
      // ONE presenter group, built from two sources:
      //  1. the conference programme (Rooms page) — everyone named in a
      //     plenary/oral/poster slot;
      //  2. paid abstract presenters — an accepted abstract's presenting
      //     author who has a paid registration, the same pairing the event
      //     page counts as "Abstract Presenters / Paid". Someone whose
      //     abstract was accepted but who never made it onto the programme
      //     still gets a presenter certificate this way.
      // Dedupe across both: by email where the programme entry was matched to
      // a registration, otherwise by name.
      const byKey = {}
      const addSlot = (person) => {
        const p = byKey[person.key]
        if (!p) {
          byKey[person.key] = {
            key: person.key, name: person.name, email: person.email,
            categories: new Set(), sessions: [], titles: [], paid: !!person.paid,
          }
          return byKey[person.key]
        }
        // An abstract-presenter registration is the authoritative email for
        // this person if the programme slot had none.
        if (!p.email && person.email) p.email = person.email
        if (person.paid) p.paid = true
        return p
      }

      this.programme.forEach(e => {
        const name = tidyName(e.presenter_name)
        if (!name) return
        const email = (e.matched_email || '').trim().toLowerCase()
        const p = addSlot({
          key: email ? `email-${email}` : `prog-${name.toLowerCase()}`,
          name, email, paid: !!e.paid,
        })
        p.categories.add(e.category)
        p.sessions.push([e.day, e.session, e.category].filter(Boolean).join(' · '))
        const title = e.title || e.activity || e.role
        if (title) p.titles.push(title)
      })

      // Plus anyone an admin set to the "Presenter" role (Edit Participant) —
      // the manual override for presenters the programme/abstracts miss.
      this.registrations
        .filter(r => (r.is_abstract_presenter && r.paid) || this.isPresenterRole(r))
        .forEach(r => {
          const name = tidyName([r.title, r.firstname, r.lastname].filter(Boolean).join(' '))
          if (!name) return
          const email = (r.email || '').trim().toLowerCase()
          // Same person as a programme slot? Then the slot's key (email-based
          // when matched, name-based otherwise) is what we have to land on.
          const existingKey = email && byKey[`email-${email}`]
            ? `email-${email}`
            : `prog-${name.toLowerCase()}`
          addSlot({ key: existingKey, name, email, paid: true })
        })

      return Object.values(byKey)
        .map(p => {
          // An abstract presenter with no programme slot has no session type to
          // show — flag the source so they're still filterable and obvious.
          const categories = new Set(p.categories)
          if (!categories.size) categories.add(ABSTRACT_ONLY_CATEGORY)
          return {
            key: p.key,
            name: p.name,
            category: p.sessions.length ? p.sessions.join(', ') : ABSTRACT_ONLY_LABEL,
            categories,
            detail: p.titles.join(' | '),
            email: p.email,
            paid: !!p.paid,
            sent: this.sentEmails.has((p.email || '').trim().toLowerCase()),
          }
        })
        .filter(p => !this.categoryFilter.length || this.categoryFilter.some(c => p.categories.has(c)))
        .sort((a, b) => a.name.localeCompare(b.name))
    },
    presenterCategories() {
      const cats = new Set(this.programme.map(e => e.category).filter(Boolean))
      if (this.presenters.some(p => p.categories.has(ABSTRACT_ONLY_CATEGORY))) {
        cats.add(ABSTRACT_ONLY_CATEGORY)
      }
      return [...cats].sort()
    },
    attendeeCategories() {
      const counts = {}
      this.registrations.forEach(r => {
        if (this.isSupportRole(r) || !r.paid) return
        if (this.isPresenter(r)) return
        const name = this.roleLabel(r)
        counts[name] = (counts[name] || 0) + 1
      })
      return Object.keys(counts).sort().map(name => ({ name, count: counts[name] }))
    },
    // Filter chips for the Presenters tab. A presenter can sit in more than
    // one category, so these counts are "rows this chip would show" and won't
    // necessarily add up to the tab total.
    presenterCategories() {
      const counts = new Map()
      this.presenters.forEach(p => p.categories.forEach(c => {
        counts.set(c, (counts.get(c) || 0) + 1)
      }))
      return [...counts.entries()]
        .sort((a, b) => a[0].localeCompare(b[0]))
        .map(([name, count]) => ({ name, count }))
    },
    filteredPeople() {
      const term = this.search.trim().toLowerCase()
      return this.people.filter(p => {
        if (this.emailOnly && !p.email) return false
        if (this.paidFilter === 'paid' && !p.paid) return false
        if (this.paidFilter === 'unpaid' && p.paid) return false
        if (this.sentFilter === 'sent' && !p.sent) return false
        if (this.sentFilter === 'unsent' && p.sent) return false
        if (!term) return true
        return p.name.toLowerCase().includes(term)
          || (p.email || '').toLowerCase().includes(term)
      })
    },
    // People on the current tab that have an email — drives the "only with
    // email" chip so the count is visible before you turn it on.
    withEmailCount() {
      return this.people.filter(p => !!p.email).length
    },
    paidCount() {
      return this.people.filter(p => p.paid).length
    },
    unpaidCount() {
      return this.people.filter(p => !p.paid).length
    },
    sentCount() {
      return this.people.filter(p => p.sent).length
    },
    notSentCount() {
      return this.people.filter(p => !p.sent).length
    },
    allShownSelected() {
      return this.filteredPeople.length > 0 && this.filteredPeople.every(p => this.selected[p.key])
    },
    selectedCount() {
      return this.people.filter(p => this.selected[p.key]).length
    },
    finalNames() {
      const names = this.people.filter(p => this.selected[p.key]).map(p => p.name)
      this.extraNames.split('\n').forEach(n => names.push(tidyName(n)))
      const seen = new Set()
      return names.filter(n => {
        const k = n.toLowerCase()
        if (!n || seen.has(k)) return false
        seen.add(k)
        return true
      })
    },
    // Only registration/programme-linked people have a known email — typed
    // "Additional names" never do, and are excluded here (they still print
    // fine via Generate, just can't be emailed automatically).
    emailableSelected() {
      return this.people.filter(p => this.selected[p.key] && p.email)
    },
    skippedNoEmailCount() {
      const selectedNoEmail = this.people.filter(p => this.selected[p.key] && !p.email).length
      const extraCount = this.extraNames.split('\n').map(n => tidyName(n)).filter(Boolean).length
      return selectedNoEmail + extraCount
    },
    // {{event}} merge tag — the selected event's display name, same text
    // shown in the "Select Event" dropdown above.
    selectedEventName() {
      const ev = this.events.find(e => String(e.id) === String(this.selectedEventId))
      return ev ? ev.event : ''
    },
    // The recipient currently picked in "Previewing as" — drives the live
    // certificate sheet in the modal, exactly as CertificatePrint renders it.
    previewName() {
      const m = this.emailModal
      if (!m) return ''
      const person = m.recipients.find(p => p.key === m.previewKey) || m.recipients[0]
      return person ? person.name : ''
    },
    // The dialog's certificate design: appreciation mode uses its own type.
    modalCertType() {
      return this.emailModal && this.emailModal.appreciation ? APPRECIATION_TYPE : this.types[this.type]
    },
    previewDesignation() {
      const m = this.emailModal
      if (!m || !m.appreciation) return ''
      const person = m.recipients.find(p => p.key === m.previewKey) || m.recipients[0]
      return person ? person.designation || '' : ''
    },
    // Driver appreciation groups — each entry has `designation` (group heading)
    // and `names`. Used by the Generate card in the template.
    appreciationDriverGroups() {
      return APPRECIATION_DRIVER_GROUPS
    },
    driverCount() {
      return APPRECIATION_DRIVER_GROUPS.reduce((n, g) => n + (g.names || []).length, 0)
    },
    // Same scaling the print page uses, sized to the modal's content width
    // (max-w-2xl) rather than the full window.
    previewScaleStyle() {
      const s = Math.min(1, 600 / 1920)
      return {
        width: `${1920 * s}px`,
        height: `${1080 * s}px`,
        '--s': s,
      }
    },
    // Subject/message with {{name}} resolved for whichever recipient is
    // currently selected in the "Previewing as" picker — recalculates as
    // the admin types, no re-render needed (only the certificate image
    // itself requires a re-render, see refreshPreview()).
    resolvedPreview() {
      const m = this.emailModal
      if (!m) return { subject: '', message: '' }
      const person = m.recipients.find(p => p.key === m.previewKey) || m.recipients[0]
      const name = person ? person.name : ''
      return {
        subject: this.renderTemplate(m.subject, name),
        message: this.renderTemplate(m.message, name),
      }
    },
  },
  mounted() {
    this.loadEvents()
  },
  methods: {
    api() {
      const api = axios.create({ baseURL: API_URL })
      if (this.authStore.accessToken) api.defaults.headers.common['Authorization'] = `Bearer ${this.authStore.accessToken}`
      return api
    },
    async loadEvents() {
      try {
        const res = await fetchData('events', 0, 100, '')
        this.events = res.data || []
        // ?event=<id> (from the event page's Certificates button) preselects the event
        const fromQuery = this.events.find(e => String(e.id) === String(this.$route.query.event))
        if (fromQuery) {
          this.selectedEventId = fromQuery.id
          this.loadPeople()
        } else if (this.events.length === 1) {
          this.selectedEventId = this.events[0].id
          this.loadPeople()
        }
      } catch (e) {
        console.error('Error loading events:', e)
      }
    },
    // Registrations come back a page at a time; the first response tells us the
    // total, so any remaining pages are all requested at once rather than one
    // after another.
    async fetchRegistrations(api, eventId) {
      const first = (await api.get(`/registrations/?event_id=${eventId}&skip=0&limit=1000`)).data
      const regs = first?.data || []
      const total = first?.total ?? regs.length
      const skips = []
      for (let skip = 1000; skip < total; skip += 1000) skips.push(skip)
      if (skips.length) {
        const pages = await Promise.all(
          skips.map(skip => api.get(`/registrations/?event_id=${eventId}&skip=${skip}&limit=1000`))
        )
        pages.forEach(p => regs.push(...(p.data?.data || [])))
      }
      return regs
    },

    // The four sources the page needs are independent, so they're fetched
    // concurrently — the page renders as soon as the slowest one lands rather
    // than the sum of all four. Each is optional: a failure in one (no
    // programme book yet, no attendance data) must not blank the page.
    async loadPeople() {
      this.registrations = []
      this.attendedRegIds = new Set()
      this.programme = []
      this.attendeeCategoryFilter = []
      this.categoryFilter = []
      this.emailOnly = this.type === 'presenter'
      this.paidFilter = ''
      this.eventLinks = []
      this.selections = { attendee: {}, presenter: {}, usher: {} }
      if (!this.selectedEventId) return
      this.isLoading = true
      const api = this.api()
      const eventId = this.selectedEventId
      try {
const [regs, attendance, programme, event, sent] = await Promise.allSettled([
        this.fetchRegistrations(api, eventId),
        api.get(`/events/${eventId}/attendance`),
        api.get(`/programme`, { params: { event_id: eventId, limit: 5000 } }),
        api.get(`/events/${eventId}`),
        api.get(`/certificates/sent`),
      ])

      if (regs.status === 'fulfilled') this.registrations = regs.value
      else console.error('Error loading registrations:', regs.reason)

      if (attendance.status === 'fulfilled') {
        const att = attendance.value.data?.data || []
        this.attendedRegIds = new Set(att.map(a => a.registration_id))
        // Default to "attended only" once the QR scans have been used.
        this.attendedOnly = this.attendedRegIds.size > 0
      }

      if (programme.status === 'fulfilled') {
        this.programme = programme.value.data?.data || []
      } else {
        console.error('Error loading programme:', programme.reason)
      }

      // Emails that already received a certificate — powers the "Sent"
      // label and Resend on each row.
      if (sent.status === 'fulfilled') {
        this.sentEmails = new Set((sent.value.data?.sent || []).map(e => String(e).trim().toLowerCase()))
      } else {
        console.error('Error loading sent certificates:', sent.reason)
      }

        // Public Links (event page's Links tab) — shown under the certificate
        // in the email preview; the actual send re-fetches these fresh
        // server-side rather than trusting this copy.
        if (event.status === 'fulfilled') {
          const links = event.value.data?.links || []
          this.eventLinks = links.filter(l => (l.access_level || 'public') === 'public')
        }
      } finally {
        this.isLoading = false
      }
    },
    setType(key) {
      this.type = key
      this.search = ''
      // Category chips are per-tab, so a chip left ticked on the tab you're
      // leaving would silently filter the tab you're arriving on.
      this.categoryFilter = []
      this.attendeeCategoryFilter = []
      // Presenters default to "Has email" — the tab is about mailing
      // certificates, and people without an address are noise here.
      this.emailOnly = key === 'presenter'
    },
    roleLabel(r) {
      return certificateCategory(r.participation_role)
    },
    isPresenterRole(r) {
      return String(r.participation_role || '').toLowerCase() === 'presenter'
    },
    presenterCategoryLabel(c) {
      return c === ABSTRACT_ONLY_CATEGORY ? 'abstract presenter' : c
    },
    // True when this registration belongs to someone already in the presenter
    // group, so they're only listed (and mailed) once, as a presenter.
    isPresenter(reg) {
      const email = (reg.email || '').trim().toLowerCase()
      if (email && this.presenterEmails.has(email)) return true
      return this.presenterNames.has(
        tidyName([reg.title, reg.firstname, reg.lastname].filter(Boolean).join(' ')).toLowerCase()
      )
    },
    // Support staff — ushers, secretariat and the media team get the same
    // certificate, so they're one group for this purpose even though they're
    // three different participation_role values. Media keep their own role
    // (and "Media" label) — they're grouped here for the certificate only.
    isSupportRole(r) {
      const role = (r.participation_role || '').toLowerCase()
      return role === 'usher' || role === 'secretariat' || role === 'media'
    },
    toggleAttendeeCategory(c) {
      const i = this.attendeeCategoryFilter.indexOf(c)
      if (i >= 0) this.attendeeCategoryFilter.splice(i, 1)
      else this.attendeeCategoryFilter.push(c)
    },
    toggleCategory(c) {
      const i = this.categoryFilter.indexOf(c)
      if (i >= 0) this.categoryFilter.splice(i, 1)
      else this.categoryFilter.push(c)
    },
    toggle(key, on) {
      this.selections[this.type] = { ...this.selected, [key]: on || undefined }
    },
    toggleAllShown(on) {
      const next = { ...this.selected }
      this.filteredPeople.forEach(p => { next[p.key] = on || undefined })
      this.selections[this.type] = next
    },
      openPrint(job) {
        // The usher/secretariat certificate names the event it supports, so the
        // print tab needs the selected event's name to render it. `designations`
        // (optional) aligns 1:1 with `names` — used by Certificates of
        // Appreciation, where each person carries a designation line.
        localStorage.setItem(CERTIFICATE_JOB_KEY, JSON.stringify({
          eventName: this.selectedEventName, ...job,
        }))
        window.open(this.$router.resolve({ name: 'CertificatePrint' }).href, '_blank')
      },
    generate() {
      if (!this.finalNames.length) return
      this.openPrint({ type: this.type, names: this.finalNames, autoPrint: true })
    },
    preview() {
      this.openPrint({ type: this.type, names: ['Full Name'], autoPrint: false })
    },
    // Certificates of Appreciation for the drivers — no emails, so straight to
    // the print tab for a one-PDF-per-page download. Uses APPRECIATION_TYPE
    // (0 CPD, "OF APPRECIATION") with each group's heading as the designation.
    generateDrivers() {
      if (!this.driverCount) return
      const names = []
      const designations = []
      APPRECIATION_DRIVER_GROUPS.forEach(g => {
        (g.names || []).forEach(n => {
          names.push(tidyName(n))
          designations.push(g.designation)
        })
      })
      this.openPrint({
        type: 'appreciation', names, designations, autoPrint: true,
      })
    },

    // html2canvas reads the live DOM, so the certificate webfonts must be
    // actually applied before rasterizing — otherwise it falls back to system
    // fonts and the 172px "Certificate" overlaps "OF PARTICIPATION".
    // Shared with the print tab; it verifies the faces really loaded.
    ensureCertFonts() {
      return ensureCertificateFonts()
    },

    // ── Email the certificate ────────────────────────────────
    // Rasterizes the hidden CertificateSheet (same markup the print page
    // uses) to a JPEG blob, at full 1920x1080 resolution.
    async renderCertificateImage(name) {
      const { jpegBlob } = await this.renderCertificateAssets(name)
      return jpegBlob
    },

    // {{name}} → the given name, everywhere it appears in a subject/message
    // template. Kept intentionally simple (one merge tag) rather than a
    // full template engine.
    renderTemplate(str, name) {
      return (str || '')
        .split('{{name}}').join(name)
        .split('{{event}}').join(this.selectedEventName || DEFAULT_EVENT_NAME)
    },

    // Opens the preview/edit modal for one person (row Send) or several
    // (bulk Email) — nothing is sent until the admin reviews and confirms.
    openEmailModal(recipients) {
      if (!recipients.length || this.emailModal) return
      this.rowMsg = null
      this.emailSuccess = ''
      this.emailModal = {
        recipients,
        subject: DEFAULT_EMAIL_SUBJECT,
        message: DEFAULT_EMAIL_MESSAGE,
        previewKey: recipients[0].key,
        rendering: false,
        sending: false,
        progressDone: 0,
        progressTotal: recipients.length,
        stage: '',
        currentName: '',
        error: '',
      }
      this.refreshPreview()
    },
    // One official from the Certificates of Appreciation card: same dialog,
    // appreciation wording/design, and an editable CC prefilled from config.
    openAppreciationModal(r) {
      if (this.emailModal) return
      this.openEmailModal([{ ...r }])
      Object.assign(this.emailModal, {
        appreciation: true,
        cc: (r.cc || []).join(', '),
        letterFile: null,
        letterError: '',
        subject: APPRECIATION_EMAIL_SUBJECT,
        message: APPRECIATION_EMAIL_MESSAGE,
      })
      this.refreshPreview()
    },
    onLetterPicked(evt) {
      const m = this.emailModal
      const file = evt.target.files && evt.target.files[0]
      evt.target.value = ''
      if (!m || !file) return
      m.letterError = ''
      if (!/\.pdf$/i.test(file.name) && file.type !== 'application/pdf') {
        m.letterError = 'Please choose a PDF file.'
        return
      }
      if (file.size > 10 * 1024 * 1024) {
        m.letterError = 'The letter must be under 10 MB.'
        return
      }
      m.letterFile = file
      if (m.message === APPRECIATION_EMAIL_MESSAGE) m.message = APPRECIATION_EMAIL_MESSAGE_LETTER
    },
    clearLetter() {
      const m = this.emailModal
      if (!m) return
      m.letterFile = null
      if (m.message === APPRECIATION_EMAIL_MESSAGE_LETTER) m.message = APPRECIATION_EMAIL_MESSAGE
    },
    closeEmailModal() {
      if (this.emailModal && this.emailModal.sending) return
      this.emailModal = null
    },
    // Link-card helpers for the modal preview — same rules as the email's
    // mailer_util._link_icon() / host line.
    linkIcon(label) {
      const l = (label || '').toLowerCase()
      if (['photo', 'picture', 'gallery', 'image'].some(k => l.includes(k))) return '📷'
      if (['presentation', 'slide', 'programme', 'program'].some(k => l.includes(k))) return '📊'
      if (['video', 'recording', 'stream', 'youtube'].some(k => l.includes(k))) return '🎥'
      return '🔗'
    },
    linkHost(url) {
      try { return new URL(url).host.replace(/^www\./, '') } catch (e) { return '' }
    },
    // Fits the live certificate sheet in the modal — the same markup the
    // print page (#/certificates/print) renders. Rasterizing is no longer
    // needed for the preview; the PDF (what's actually attached) is still
    // built at send time in doSendOne/doEmailBulk.
    async refreshPreview() {
      const m = this.emailModal
      if (!m) return
      m.rendering = true
      try {
        await this.ensureCertFonts()
        await this.$nextTick()
        const sheet = this.$refs.previewSheet
        if (sheet && sheet.fitName) { sheet.fitName(); sheet.fitBody() }
      } finally {
        if (this.emailModal === m) m.rendering = false
      }
    },

    async confirmSendEmail() {
      const m = this.emailModal
      if (!m || m.sending) return
      m.sending = true
      m.error = ''
      m.progressDone = 0
      m.stage = ''
      m.currentName = ''
      try {
        if (m.recipients.length === 1) {
          const p = m.recipients[0]
          await this.doSendOne(p, m.subject, m.message)
          this.sentEmails.add((p.email || '').trim().toLowerCase())
          this.emailSuccess = `Sent to ${p.email}.`
        } else {
          const { queued, skipped } = await this.doEmailBulk(m, m.subject, m.message)
          m.recipients.forEach(p => this.sentEmails.add((p.email || '').trim().toLowerCase()))
          this.emailSuccess = `Queued ${queued} certificate email${queued === 1 ? '' : 's'}.` +
            (skipped ? ` ${skipped} skipped (no image/email matched).` : '')
        }
        this.closeEmailModal()
      } catch (e) {
        m.error = e.response?.data?.detail || 'Failed to send.'
      } finally {
        if (this.emailModal === m) m.sending = false
      }
    },

    // ── Email the certificate ────────────────────────────────
    // Rasterizes the hidden CertificateSheet (same markup the print page
    // uses) via the browser's own layout engine, once, then derives both:
    //  - jpegBlob: shown inline in the email body (what the recipient sees
    //    without opening anything — email clients can't render a PDF inline)
    //  - pdfBlob: a full-bleed single-page PDF at the certificate's exact
    //    1920x1080 design size — the actual file attached/kept, same
    //    approach as the per-room PDF export on the Rooms page.
    //
    // Native SVG foreignObject rasterization is used (NOT html2canvas):
    // html2canvas re-draws fonts and can misalign the 172px "Certificate"
    // heading over "OF PARTICIPATION". foreignObject asks the browser to
    // lay out the live sheet exactly as the preview/print page renders it,
    // so the emailed image is pixel-identical to what the admin previewed.
    async renderCertificateAssets(name, opts = {}) {
      this.renderJob = { name, type: opts.type || this.types[this.type], designation: opts.designation || '' }
      await this.$nextTick()
      await this.ensureCertFonts()
      const sheet = this.$refs.renderSheet
      if (sheet && sheet.fitName) { sheet.fitName(); sheet.fitBody() }
      await this.$nextTick()

      const canvas = await this.rasterizeElementNative(sheet.$el, 1920, 1080)
      const jpegBlob = await new Promise(resolve => canvas.toBlob(resolve, 'image/jpeg', 0.85))

      const jsMod = await import('jspdf')
      const JsPDF = jsMod.jsPDF || (jsMod.default && jsMod.default.jsPDF) || jsMod.default
      const pdf = new JsPDF({ unit: 'px', format: [1920, 1080], orientation: 'landscape', hotfixes: ['px_scaling'] })
      pdf.addImage(canvas.toDataURL('image/jpeg', 0.92), 'JPEG', 0, 0, 1920, 1080, undefined, 'FAST')
      const pdfBlob = pdf.output('blob')

      return { jpegBlob, pdfBlob }
    },

    // Render a DOM element to a canvas using SVG foreignObject — the browser
    // lays out the element's own HTML/CSS (webfonts, images, SVG, canvas
    // children all included) and rasterizes that, so output matches the
    // on-screen preview exactly rather than a re-parse. Fonts and images are
    // inlined as data URLs because an SVG loaded as an image must not fetch
    // any external resource (the browser blocks them) — the certificate's
    // webfonts would silently fall back and "Certificate" would collide with
    // "OF PARTICIPATION", exactly the bug html2canvas produced.
    async rasterizeElementNative(el, width, height) {
      const clone = el.cloneNode(true)

      // Bake the live computed styles into the clone. Inside the SVG only
      // inline styles apply — Tailwind's preflight (margin:0, line-height:1.5,
      // box-sizing…) and the sheet's scoped `margin:0` are gone, so default
      // h1/h3/p margins pushed every text block down onto the rules/signature.
      this.inlineComputedStyles(el, clone)

      // <canvas> pixels aren't copied by cloneNode — swap each for an <img>.
      const srcCanvases = el.querySelectorAll('canvas')
      clone.querySelectorAll('canvas').forEach((c, i) => {
        const img = document.createElement('img')
        try { img.setAttribute('src', srcCanvases[i].toDataURL('image/png')) } catch (e) { return }
        img.setAttribute('style', c.getAttribute('style') || '')
        c.replaceWith(img)
      })

      // Inline <img> sources so they survive inside the SVG-as-image context.
      const imgs = [...clone.querySelectorAll('img')]
      await Promise.all(imgs.map(async (img) => {
        const src = img.getAttribute('src')
        if (!src || src.startsWith('data:')) return
        try {
          const res = await fetch(src)
          const blob = await res.blob()
          const dataUrl = await new Promise(r => {
            const fr = new FileReader()
            fr.onload = () => r(fr.result)
            fr.readAsDataURL(blob)
          })
          img.setAttribute('src', dataUrl)
        } catch (e) { /* leave as-is if it can't be fetched */ }
      }))

      // Inline the certificate @font-face rules as data URLs, emitted as a
      // <style> inside the foreignObject so the layout engine has the real
      // webfonts (Alex Brush / Montserrat / Playfair Display) available.
      const fontCss = await this.inlineCertificateFonts()

      const styleBlock = fontCss ? `<style>${fontCss}</style>` : ''
      // Serialize through XMLSerializer, not outerHTML: outerHTML emits HTML
      // entities (e.g. the &nbsp; run in the college header) that are invalid
      // in an XML/SVG document and would make the SVG fail to parse.
      const wrapper = document.createElementNS('http://www.w3.org/1999/xhtml', 'div')
      wrapper.appendChild(clone)
      const inner = new XMLSerializer().serializeToString(wrapper)
      const svg = [
        `<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}">`,
        `<foreignObject width="100%" height="100%">`,
        `<div xmlns="http://www.w3.org/1999/xhtml">${styleBlock}${inner}</div>`,
        `</foreignObject>`,
        `</svg>`,
      ].join('')
      // Must be a data: URI, NOT a blob: URL — a blob URL makes the browser
      // treat the SVG as cross-origin and taint the canvas, so toBlob() throws
      // SecurityError and the send fails ("Failed to send."). A data URI keeps
      // it same-origin and the canvas is exportable.
      const url = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(svg)
      try {
        const img = new Image()
        img.decoding = 'async'
        await new Promise((resolve, reject) => {
          img.onload = resolve
          img.onerror = reject
          img.src = url
        })
        const canvas = document.createElement('canvas')
        canvas.width = width
        canvas.height = height
        const ctx = canvas.getContext('2d')
        ctx.drawImage(img, 0, 0, width, height)
        return canvas
      } catch (e) {
        // Fall back to html2canvas only if this browser can't render the
        // foreignObject SVG (rare); html2canvas's own font measurement can
        // shift script fonts, but it still produces a usable certificate.
        const hcMod = await import('html2canvas')
        const html2canvas = hcMod.default || hcMod
        return html2canvas(el, {
          scale: 1, useCORS: true, backgroundColor: '#ffffff', logging: false,
          width, height,
        })
      }
    },

    // Copies the layout/typography properties the browser actually resolved
    // for each HTML element (and each root <svg>) of `src` onto the matching
    // node of `dst` (a cloneNode of src, so the trees line up 1:1). SVG
    // internals are skipped — their presentation attributes travel with them.
    inlineComputedStyles(src, dst) {
      const props = [
        'display', 'box-sizing', 'margin-top', 'margin-right', 'margin-bottom', 'margin-left',
        'padding-top', 'padding-right', 'padding-bottom', 'padding-left',
        'border-top-width', 'border-right-width', 'border-bottom-width', 'border-left-width',
        'border-top-style', 'border-right-style', 'border-bottom-style', 'border-left-style',
        'border-top-color', 'border-right-color', 'border-bottom-color', 'border-left-color',
        'font-family', 'font-size', 'font-weight', 'font-style', 'line-height',
        'letter-spacing', 'word-spacing', 'text-align', 'text-transform', 'white-space',
        'color', 'vertical-align', 'max-width', 'overflow',
      ]
      const walk = (s, d) => {
        const isSvgChild = s.namespaceURI === 'http://www.w3.org/2000/svg' && s.parentElement &&
          s.parentElement.namespaceURI === 'http://www.w3.org/2000/svg'
        if (isSvgChild) return
        const cs = getComputedStyle(s)
        props.forEach(p => d.style.setProperty(p, cs.getPropertyValue(p)))
        for (let i = 0; i < s.children.length; i++) {
          if (d.children[i]) walk(s.children[i], d.children[i])
        }
      }
      walk(src, dst)
    },

    // Pull every @font-face rule for the certificate families out of the
    // live stylesheets and rewrite its src to a data URL, so the font is
    // embedded directly in the SVG (an SVG loaded as an image can't fetch
    // the font file itself).
    async inlineCertificateFonts() {
      const wanted = ['Alex Brush', 'Montserrat', 'Playfair Display']
      const rules = []
      const seen = new Set()
      const sheets = [...document.styleSheets]
      for (const sheet of sheets) {
        let cssRules
        try { cssRules = sheet.cssRules } catch (e) { continue }
        for (const rule of cssRules) {
          if (!rule || rule.type !== CSSRule.FONT_FACE_RULE) continue
          const family = ((rule.style && rule.style.fontFamily) || '').replace(/["']/g, '').trim()
          if (!wanted.some(f => family.startsWith(f))) continue
          const cssText = rule.cssText
          if (seen.has(cssText)) continue
          seen.add(cssText)
          const m = cssText.match(/url\((['"]?)([^'")]+)\1\)/)
          let text = cssText
          if (m && !m[2].startsWith('data:')) {
            try {
              const res = await fetch(m[2])
              const blob = await res.blob()
              const dataUrl = await new Promise(r => {
                const fr = new FileReader()
                fr.onload = () => r(fr.result)
                fr.readAsDataURL(blob)
              })
              text = cssText.replace(m[0], `url(${dataUrl})`)
            } catch (e) { /* keep original rule if fetch fails */ }
          }
          rules.push(text)
        }
      }
      return rules.join('\n')
    },

    async doSendOne(p, subjectTpl, messageTpl) {
      this.rowMsg = null
      const m = this.emailModal
      if (m) { m.stage = 'Preparing certificate…'; m.currentName = `${p.name} — ${p.email}` }
      const appreciation = !!(m && m.appreciation)
      const { jpegBlob, pdfBlob } = await this.renderCertificateAssets(
        p.name, appreciation ? { type: APPRECIATION_TYPE, designation: p.designation } : {},
      )
      if (m) m.stage = 'Sending email…'
      const form = new FormData()
      form.append('recipient_email', p.email)
      form.append('recipient_name', p.name)
      form.append('event_id', this.selectedEventId)
      form.append('subject', this.renderTemplate(subjectTpl, p.name))
      form.append('message', this.renderTemplate(messageTpl, p.name))
      form.append('image', jpegBlob, 'certificate.jpg')
      form.append('pdf', pdfBlob, 'certificate.pdf')
      if (appreciation) {
        form.append('cc', m.cc || '')
        form.append('kind', 'appreciation')
        if (m.letterFile) form.append('attachment', m.letterFile, m.letterFile.name)
      }
      await this.api().post('/certificates/send', form)
      this.rowMsg = { key: p.key, ok: true, text: 'Sent' }
    },

    async doEmailBulk(modal, subjectTpl, messageTpl) {
      const recipients = modal.recipients
      let queued = 0
      let skipped = 0
      for (let start = 0; start < recipients.length; start += EMAIL_BATCH_SIZE) {
        const batch = recipients.slice(start, start + EMAIL_BATCH_SIZE)
        const form = new FormData()
        const manifest = []
        for (const p of batch) {
          modal.stage = `Preparing certificate ${modal.progressDone + 1} of ${modal.progressTotal}`
          modal.currentName = p.name
          const { jpegBlob, pdfBlob } = await this.renderCertificateAssets(p.name)
          const base = p.key.replace(/[^A-Za-z0-9_-]+/g, '_')
          const filename = `${base}.jpg`
          const pdfFilename = `${base}.pdf`
          form.append('images', jpegBlob, filename)
          form.append('pdfs', pdfBlob, pdfFilename)
          manifest.push({
            filename, pdf_filename: pdfFilename, email: p.email, name: p.name,
            subject: this.renderTemplate(subjectTpl, p.name),
            message: this.renderTemplate(messageTpl, p.name),
          })
          modal.progressDone++
        }
        modal.stage = `Uploading ${batch.length} certificate${batch.length === 1 ? '' : 's'}…`
        modal.currentName = ''
        form.append('manifest', JSON.stringify(manifest))
        form.append('event_id', this.selectedEventId)
        const res = await this.api().post('/certificates/send-bulk', form)
        queued += res.data?.queued || 0
        skipped += res.data?.skipped || 0
      }
      return { queued, skipped }
    },
  },
}
</script>

<style scoped>
/* Scale the live certificate sheet in the email preview the same way the
   print page does (#/certificates/print): the sheet stays 1920x1080 and is
   shrunk with a CSS transform, so the on-screen preview is pixel-identical
   to what gets printed/emailed. */
.cert-preview-scaled {
  overflow: hidden;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}
.cert-preview-scaled > .cert {
  width: 1920px;
  height: 1080px;
  transform: scale(var(--s, 0.3125));
  transform-origin: top left;
}
</style>
