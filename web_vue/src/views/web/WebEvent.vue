<template>
  <div class="bg-gray-50 text-gray-800 min-h-screen">

    <!-- ─── Hero Banner ──────────────────────────────────────────────────────── -->
    <section class="relative w-full overflow-hidden" style="min-height: 340px;">
      <div class="absolute inset-0 bg-center bg-cover" :style="heroBgStyle"></div>
      <div class="absolute inset-0" :style="heroOverlayStyle"></div>

      <div class="relative z-10 max-w-4xl mx-auto px-6 py-14 sm:py-20 text-white text-center">
        <div v-if="event.org_unit" class="mb-3 text-sm font-semibold text-white/80">
          Organised by {{ event.org_unit }}
        </div>
        <h1 class="text-3xl sm:text-4xl font-bold tracking-tight mb-3 drop-shadow-md"
          v-html="formatOrdinals(event.event || '')"></h1>
        <p class="text-base text-white/90 mb-6">
          {{ formatDate(event.start_date) }} – {{ formatDate(event.end_date) }}
          &middot; {{ event.location }}
        </p>
        <div class="flex flex-wrap justify-center gap-3">
          <!-- Already registered -->
          <span v-if="userAccess !== 'none'"
            class="inline-flex items-center gap-2 bg-white/20 text-white/70 font-semibold px-7 py-2.5 rounded-full cursor-not-allowed select-none">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
            Already Registered
          </span>
          <!-- Registration open & not yet registered -->
          <router-link v-else-if="isRegistrationOpen"
            :to="{ name: 'EventRegister', params: { id: event.id } }"
            class="inline-block font-semibold px-7 py-2.5 rounded-full shadow transition hover:opacity-90"
            style="background-color: rgb(254,80,103); color: #fff;">
            Register Now →
          </router-link>
          <!-- Registration closed -->
          <span v-else
            class="inline-block bg-white/20 text-white/60 font-semibold px-7 py-2.5 rounded-full cursor-not-allowed">
            Registration Closed
          </span>
        </div>
      </div>
    </section>

    <!-- ─── Loading ──────────────────────────────────────────────────────────── -->
    <div v-if="isLoading" class="flex justify-center py-20">
      <svg class="animate-spin h-10 w-10" style="color: rgb(254,80,103);" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
      </svg>
    </div>

    <!-- ─── Main Content ──────────────────────────────────────────────────────── -->
    <section v-else class="max-w-5xl mx-auto px-6 py-10 space-y-8">

      <!-- ── Event Details ──────────────────────────────────────────────────── -->
      <section class="bg-white rounded-2xl shadow-sm overflow-hidden">
        <div class="px-6 py-4 flex items-center gap-3 border-b border-gray-100">
          <div class="h-10 w-10 rounded-xl flex items-center justify-center flex-shrink-0"
            style="background-color: rgb(254,80,103);">
            <svg class="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h2 class="text-xl font-bold" style="color: rgb(254,80,103);">Event Details</h2>
        </div>
        <div class="px-6 py-5">
          <dl class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <!-- Theme -->
            <div v-if="event.theme" class="flex items-start gap-3 p-3 rounded-xl bg-gray-50">
              <div class="h-8 w-8 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5"
                style="background-color: rgba(254,80,103,0.12);">
                <svg class="w-4 h-4" style="color: rgb(254,80,103);" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z" />
                </svg>
              </div>
              <div>
                <dt class="text-xs font-semibold uppercase tracking-wide text-gray-400 mb-0.5">Theme</dt>
                <dd class="text-gray-800 font-medium text-sm leading-snug">{{ event.theme }}</dd>
              </div>
            </div>
            <!-- Location -->
            <div class="flex items-start gap-3 p-3 rounded-xl bg-gray-50">
              <div class="h-8 w-8 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5"
                style="background-color: rgba(220,50,75,0.12);">
                <svg class="w-4 h-4" style="color: rgb(220,50,75);" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
              </div>
              <div>
                <dt class="text-xs font-semibold uppercase tracking-wide text-gray-400 mb-0.5">Location</dt>
                <dd class="text-gray-800 font-medium text-sm">{{ event.location || '—' }}</dd>
              </div>
            </div>
            <!-- Start Date -->
            <div class="flex items-start gap-3 p-3 rounded-xl bg-gray-50">
              <div class="h-8 w-8 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5"
                style="background-color: rgba(254,80,103,0.12);">
                <svg class="w-4 h-4" style="color: rgb(254,80,103);" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
              </div>
              <div>
                <dt class="text-xs font-semibold uppercase tracking-wide text-gray-400 mb-0.5">Start Date</dt>
                <dd class="text-gray-800 font-medium text-sm">{{ formatDate(event.start_date) }}</dd>
              </div>
            </div>
            <!-- End Date -->
            <div class="flex items-start gap-3 p-3 rounded-xl bg-gray-50">
              <div class="h-8 w-8 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5"
                style="background-color: rgba(220,50,75,0.12);">
                <svg class="w-4 h-4" style="color: rgb(220,50,75);" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
              </div>
              <div>
                <dt class="text-xs font-semibold uppercase tracking-wide text-gray-400 mb-0.5">End Date</dt>
                <dd class="text-gray-800 font-medium text-sm">{{ formatDate(event.end_date) }}</dd>
              </div>
            </div>
            <!-- Organised By -->
            <div v-if="event.org_unit" class="flex items-start gap-3 p-3 rounded-xl bg-gray-50">
              <div class="h-8 w-8 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5"
                style="background-color: rgba(254,80,103,0.12);">
                <svg class="w-4 h-4" style="color: rgb(254,80,103);" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                </svg>
              </div>
              <div>
                <dt class="text-xs font-semibold uppercase tracking-wide text-gray-400 mb-0.5">Organised By</dt>
                <dd class="font-semibold text-sm" style="color: rgb(254,80,103);">{{ event.org_unit }}</dd>
              </div>
            </div>
            <!-- Country -->
            <div v-if="event.country" class="flex items-start gap-3 p-3 rounded-xl bg-gray-50">
              <div class="h-8 w-8 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5"
                style="background-color: rgba(220,50,75,0.12);">
                <svg class="w-4 h-4" style="color: rgb(220,50,75);" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M3 21v-4m0 0V5a2 2 0 012-2h6.5l1 1H21l-3 6 3 6h-8.5l-1-1H5a2 2 0 00-2 2zm9-13.5V9" />
                </svg>
              </div>
              <div>
                <dt class="text-xs font-semibold uppercase tracking-wide text-gray-400 mb-0.5">Country</dt>
                <dd class="text-gray-800 font-medium text-sm">{{ event.country }}</dd>
              </div>
            </div>
          </dl>
        </div>
      </section>

      <!-- ── Description ────────────────────────────────────────────────────── -->
      <section v-if="event.description" class="bg-white rounded-2xl shadow-sm overflow-hidden">
        <div class="px-6 py-4 flex items-center gap-3 border-b border-gray-100">
          <div class="h-10 w-10 rounded-xl flex items-center justify-center flex-shrink-0"
            style="background-color: rgb(254,80,103);">
            <svg class="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <h2 class="text-xl font-bold" style="color: rgb(254,80,103);">About This Event</h2>
        </div>
        <div class="px-6 py-5">
          <p class="text-gray-700 leading-relaxed whitespace-pre-line">{{ event.description }}</p>
        </div>
      </section>

      <!-- ── Organizers ─────────────────────────────────────────────────────── -->
      <section v-if="event.organizers" class="bg-white rounded-2xl shadow-sm overflow-hidden">
        <div class="px-6 py-4 flex items-center gap-3 border-b border-gray-100">
          <div class="h-10 w-10 rounded-xl flex items-center justify-center flex-shrink-0"
            style="background-color: rgb(254,80,103);">
            <svg class="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
          </div>
          <h2 class="text-xl font-bold" style="color: rgb(254,80,103);">Organizers</h2>
        </div>
        <div class="px-6 py-5">
          <p class="text-gray-700 leading-relaxed whitespace-pre-line">{{ event.organizers }}</p>
        </div>
      </section>

      <!-- ── Participation Categories & Fees ────────────────────────────────── -->
      <section v-if="participationCategories.length">
        <div class="px-6 py-4 flex items-center gap-3 rounded-t-2xl"
          style="background-color: rgb(254,80,103);">
          <svg class="w-6 h-6 text-white flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M15 5v2m0 4v2m0 4v2M5 5a2 2 0 00-2 2v3a2 2 0 110 4v3a2 2 0 002 2h14a2 2 0 002-2v-3a2 2 0 110-4V7a2 2 0 00-2-2H5z" />
          </svg>
          <h2 class="text-xl font-bold text-white">Participation Categories &amp; Conference Fees</h2>
        </div>
        <div class="grid grid-cols-2 sm:grid-cols-3 gap-px bg-gray-200">
          <div v-for="cat in participationCategories" :key="cat.name"
            class="flex flex-col items-center justify-between p-6 text-center"
            style="background-color: rgb(254,80,103);">
            <div class="h-12 w-12 rounded-full bg-white/15 flex items-center justify-center mb-3">
              <svg class="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                  d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
            </div>
            <h3 class="text-white font-bold text-base leading-snug mb-4 min-h-[2.5rem] flex items-center">{{ cat.name }}</h3>
            <span class="inline-block px-5 py-2 font-bold text-sm rounded-sm shadow"
              style="background-color: #fff; color: rgb(254,80,103);">{{ cat.fee }}</span>
          </div>
        </div>
        <div v-if="participationNote"
          class="flex items-center gap-2 px-5 py-3 text-sm font-medium text-white rounded-b-2xl"
          style="background-color: rgb(220,50,75);">
          <svg class="w-4 h-4 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd"
              d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
              clip-rule="evenodd" />
          </svg>
          {{ participationNote }}
        </div>
      </section>

      <!-- ── Logistics Accordion ────────────────────────────────────────────── -->
      <section v-if="logisticsSections.length">
        <div class="px-6 py-4 flex items-center gap-3 rounded-t-2xl"
          style="background-color: rgb(254,80,103);">
          <svg class="w-6 h-6 text-white flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
          </svg>
          <h2 class="text-xl font-bold text-white">Logistics Information</h2>
        </div>
        <div class="border border-t-0 border-gray-200 divide-y divide-gray-200 bg-white rounded-b-2xl overflow-hidden">
          <div v-for="(sec, i) in logisticsSections" :key="i">
            <button @click="toggleLogistics(i)"
              class="w-full flex items-center justify-between px-6 py-4 text-left font-semibold text-base transition-colors"
              :style="openLogistics === i
                ? 'background-color: rgb(220,50,75); color: #fff;'
                : 'background-color: #f8fafc; color: #374151;'">
              <span>{{ sec.title }}</span>
              <svg class="w-5 h-5 flex-shrink-0 transition-transform duration-200"
                :class="openLogistics === i ? 'rotate-180' : ''"
                fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
              </svg>
            </button>
            <div v-show="openLogistics === i"
              class="px-6 py-5 bg-white text-gray-700 text-sm leading-relaxed whitespace-pre-line border-t border-gray-100">
              {{ sec.content }}
            </div>
          </div>
        </div>
      </section>

      <!-- ── Downloads ──────────────────────────────────────────────────────── -->
      <section class="bg-white rounded-2xl shadow-sm overflow-hidden">
        <div class="px-6 py-4 flex items-center gap-3 border-b border-gray-100">
          <div class="h-10 w-10 rounded-xl flex items-center justify-center flex-shrink-0"
            style="background-color: rgb(254,80,103);">
            <svg class="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
          </div>
          <h2 class="text-xl font-bold" style="color: rgb(254,80,103);">Downloads</h2>
        </div>
        <div class="px-6 py-5">
          <!-- Paid — show files -->
          <div v-if="userAccess === 'paid' && documents.length">
            <ul class="space-y-2">
              <li v-for="file in documents" :key="file.id"
                class="flex items-center gap-3 p-3 rounded-xl bg-gray-50 hover:bg-gray-100 transition">
                <div class="h-8 w-8 rounded-lg flex items-center justify-center flex-shrink-0"
                  style="background-color: rgb(254,80,103);">
                  <svg class="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                  </svg>
                </div>
                <a :href="`${apiUrl}/${file.path}`" target="_blank"
                  class="text-sm font-semibold hover:underline" style="color: rgb(254,80,103);">
                  {{ file.name }}
                </a>
              </li>
            </ul>
          </div>
          <!-- Paid but no files -->
          <div v-else-if="userAccess === 'paid' && !documents.length"
            class="text-sm text-gray-400 italic">No downloads available yet.</div>
          <!-- Logged in but unpaid -->
          <div v-else-if="userAccess === 'unpaid'"
            class="flex items-start gap-4 rounded-xl p-4 border-2"
            style="border-color: rgba(254,80,103,0.4); background-color: rgba(254,80,103,0.05);">
            <div class="h-10 w-10 rounded-xl flex items-center justify-center flex-shrink-0 mt-0.5"
              style="background-color: rgb(254,80,103);">
              <svg class="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
            </div>
            <div>
              <p class="font-semibold text-gray-800 text-sm">Payment Required</p>
              <p class="text-gray-500 text-sm mt-0.5">Documents are available to registered participants who have completed payment.</p>
              <router-link :to="{ name: 'EventRegister', params: { id: event.id } }"
                class="inline-block mt-3 px-4 py-2 rounded-full text-xs font-bold text-white transition hover:opacity-90"
                style="background-color: rgb(254,80,103);">
                Register &amp; Pay →
              </router-link>
            </div>
          </div>
          <!-- Not logged in -->
          <div v-else class="flex items-start gap-4 rounded-xl p-4 border-2 border-gray-200 bg-gray-50">
            <div class="h-10 w-10 rounded-xl flex items-center justify-center flex-shrink-0 mt-0.5 bg-gray-300">
              <svg class="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
            </div>
            <div>
              <p class="font-semibold text-gray-700 text-sm">Members Only</p>
              <p class="text-gray-500 text-sm mt-0.5">
                Downloads are available to paid participants only.
                Please <router-link :to="{ name: 'Login' }" class="underline font-semibold"
                  style="color: rgb(254,80,103);">log in</router-link>
                and ensure your registration is complete.
              </p>
            </div>
          </div>
        </div>
      </section>

      <!-- ── Useful Links ───────────────────────────────────────────────────── -->
      <section class="bg-white rounded-2xl shadow-sm overflow-hidden">
        <div class="px-6 py-4 flex items-center gap-3 border-b border-gray-100">
          <div class="h-10 w-10 rounded-xl flex items-center justify-center flex-shrink-0"
            style="background-color: rgb(220,50,75);">
            <svg class="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
            </svg>
          </div>
          <h2 class="text-xl font-bold" style="color: rgb(220,50,75);">Useful Links</h2>
        </div>
        <div class="px-6 py-5">
          <!-- Paid — show links -->
          <div v-if="userAccess === 'paid' && links.length">
            <ul class="space-y-2">
              <li v-for="link in links" :key="link.id"
                class="flex items-center gap-3 p-3 rounded-xl bg-gray-50 hover:bg-gray-100 transition">
                <div class="h-8 w-8 rounded-lg flex items-center justify-center flex-shrink-0"
                  style="background-color: rgb(220,50,75);">
                  <svg class="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                  </svg>
                </div>
                <a :href="link.link" target="_blank"
                  class="text-sm font-semibold hover:underline" style="color: rgb(220,50,75);">
                  {{ link.link_name || link.name }}
                </a>
              </li>
            </ul>
          </div>
          <!-- Paid but no links -->
          <div v-else-if="userAccess === 'paid' && !links.length"
            class="text-sm text-gray-400 italic">No links available yet.</div>
          <!-- Logged in but unpaid -->
          <div v-else-if="userAccess === 'unpaid'"
            class="flex items-start gap-4 rounded-xl p-4 border-2"
            style="border-color: rgba(220,50,75,0.4); background-color: rgba(220,50,75,0.05);">
            <div class="h-10 w-10 rounded-xl flex items-center justify-center flex-shrink-0 mt-0.5"
              style="background-color: rgb(220,50,75);">
              <svg class="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
            </div>
            <div>
              <p class="font-semibold text-gray-800 text-sm">Payment Required</p>
              <p class="text-gray-500 text-sm mt-0.5">Resource links are available to registered participants who have completed payment.</p>
              <router-link :to="{ name: 'EventRegister', params: { id: event.id } }"
                class="inline-block mt-3 px-4 py-2 rounded-full text-xs font-bold text-white transition hover:opacity-90"
                style="background-color: rgb(220,50,75);">
                Register &amp; Pay →
              </router-link>
            </div>
          </div>
          <!-- Not logged in -->
          <div v-else class="flex items-start gap-4 rounded-xl p-4 border-2 border-gray-200 bg-gray-50">
            <div class="h-10 w-10 rounded-xl flex items-center justify-center flex-shrink-0 mt-0.5 bg-gray-300">
              <svg class="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
            </div>
            <div>
              <p class="font-semibold text-gray-700 text-sm">Members Only</p>
              <p class="text-gray-500 text-sm mt-0.5">
                Useful links are available to paid participants only.
                Please <router-link :to="{ name: 'Login' }" class="underline font-semibold"
                  style="color: rgb(254,80,103);">log in</router-link>
                and ensure your registration is complete.
              </p>
            </div>
          </div>
        </div>
      </section>

    </section>
  </div>
</template>

<script>
import { fetchItem } from '@/services/apiService'

export default {
  name: 'WebEventView',
  data() {
    return {
      isLoading: true,
      event: {},
      documents: [],
      links: [],
      userAccess: 'none',
      openLogistics: 0,
      apiUrl: import.meta.env.VITE_API_URL,
    }
  },
  computed: {
    heroBgStyle() {
      if (this.event.banner_image) {
        return { backgroundImage: `url('${this.apiUrl}/${this.event.banner_image}')` }
      }
      return { background: 'linear-gradient(135deg, rgb(254,80,103) 0%, rgb(100,20,40) 100%)' }
    },
    heroOverlayStyle() {
      const opacity = this.event.banner_image ? '0.55' : '0.30'
      return { backgroundColor: `rgba(0,0,0,${opacity})` }
    },
    isRegistrationOpen() {
      if (!this.event.start_date) return false
      const diffDays = (new Date(this.event.start_date) - new Date()) / (1000 * 60 * 60 * 24)
      return diffDays >= 0
    },
    participationCategories() {
      const raw = this.event.participation_info || ''
      if (!raw) return []
      const lines = raw.split('\n').map(l => l.trim()).filter(Boolean)
      const cats = []
      for (const line of lines) {
        if (line === '---') break
        const parts = line.split('|')
        if (parts.length >= 2) cats.push({ name: parts[0].trim(), fee: parts[1].trim() })
      }
      return cats
    },
    participationNote() {
      const raw = this.event.participation_info || ''
      if (!raw) return ''
      const idx = raw.indexOf('---')
      if (idx === -1) return ''
      return raw.slice(idx + 3).trim().replace(/\n/g, ' ')
    },
    logisticsSections() {
      const raw = this.event.logistics_info || ''
      if (!raw) return []
      return raw
        .split(/\n##\s+/)
        .filter(Boolean)
        .map(block => {
          const nl = block.indexOf('\n')
          if (nl === -1) return { title: block.replace(/^##\s*/, '').trim(), content: '' }
          return {
            title: block.slice(0, nl).replace(/^##\s*/, '').trim(),
            content: block.slice(nl + 1).trim()
          }
        })
        .filter(s => s.title)
    }
  },
  async mounted() {
    const id = this.$route.params.id
    try {
      const res = await fetchItem('events', id)
      this.event = res.event || {}
      this.documents = res.documents || []
      this.links = res.links || []
      this.userAccess = res.event?.user_access || 'none'
    } catch (e) {
      console.error('Error fetching event:', e)
    } finally {
      this.isLoading = false
    }
  },
  methods: {
    formatDate(d) {
      if (!d) return '—'
      return new Date(d).toLocaleDateString(undefined, { year: 'numeric', month: 'long', day: 'numeric' })
    },
    formatOrdinals(text) {
      if (!text) return ''
      return text.replace(/(\d+)(st|nd|rd|th)\b/gi, (_, num, suffix) =>
        `${num}<sup style="font-size:0.55em;vertical-align:super;">${suffix}</sup>`)
    },
    toggleLogistics(i) {
      this.openLogistics = this.openLogistics === i ? -1 : i
    }
  }
}
</script>

<style scoped>
.rotate-180 { transform: rotate(180deg); }
</style>
