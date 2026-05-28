import { createRouter, createWebHashHistory } from "vue-router";
import MainLayout from "@/layouts/MainLayout.vue";
import WebLayout from "@/layouts/WebLayout.vue";
import MyAccountLayout from "@/layouts/MyAccountLayout.vue";
import NotFoundView from "@/views/NotFound.vue";
import { useAuthStore } from "@/store/authStore";

const routeComponents = {
  MainLayout,
  WebLayout,
  MyAccountLayout,
  HomeView: () => import("@/views/web/Home.vue"),
  LoginView: () => import("@/views/auth/Login.vue"),
  RegisterView: () => import("@/views/auth/Register.vue"),
  EventRegisterView: () => import("@/views/web/Register.vue"),
  PaymentView: () => import("@/views/web/Payment.vue"),
  ResetPasswordView: () => import("@/views/auth/ResetPassword.vue"),
  DashboardView: () => import("@/views/main/dashboard/Dashboard.vue"),
  WebEventsView: () => import("@/views/web/WebEvents.vue"),
  WebEventView: () => import("@/views/web/WebEvent.vue"),
  UserEventStatusView: () => import("@/views/web/UserEventStatus.vue"),
  AttendanceView: () => import("@/views/web/Attendance.vue"),

  EventsView: () => import("@/views/main/events/Events.vue"),
  AddEventView: () => import("@/views/main/events/Add.vue"),
  EventView: () => import("@/views/main/events/Event.vue"),
  EditEventView: () => import("@/views/main/events/Edit.vue"),
  AccessEventView: () => import("@/views/main/events/AccessEvent.vue"),

  ParticipantsView: () => import("@/views/main/participants/Participants.vue"),
  AddParticipantView: () => import("@/views/main/participants/Add.vue"),
  ParticipantView: () => import("@/views/main/participants/Participant.vue"),
  EditParticipantView: () => import("@/views/main/participants/Edit.vue"),

  ConfigurationsView: () =>
    import("@/views/main/configurations/Configurations.vue"),
  ContactsView: () => import("@/views/main/configurations/Contacts.vue"),
  EmailTemplatesView: () =>
    import("@/views/main/configurations/EmailTemplates.vue"),

  UsersView: () => import("@/views/main/configurations/users/Users.vue"),
  AddUserView: () => import("@/views/main/configurations/users/Add.vue"),
  UserView: () => import("@/views/main/configurations/users/User.vue"),
  EditUserView: () => import("@/views/main/configurations/users/Edit.vue"),

  RolesView: () => import("@/views/main/configurations/roles/Roles.vue"),
  AddRoleView: () => import("@/views/main/configurations/roles/Add.vue"),
  RoleView: () => import("@/views/main/configurations/roles/Role.vue"),
  EditRoleView: () => import("@/views/main/configurations/roles/Edit.vue"),

  EventTypesView: () =>
    import("@/views/main/configurations/event-types/EventTypes.vue"),
  AddEventTypeView: () =>
    import("@/views/main/configurations/event-types/Add.vue"),
  EditEventTypeView: () =>
    import("@/views/main/configurations/event-types/Edit.vue"),

  OrganisersView: () =>
    import("@/views/main/configurations/organisers/Organisers.vue"),
  AddOrganiserView: () =>
    import("@/views/main/configurations/organisers/Add.vue"),
  EditOrganiserView: () =>
    import("@/views/main/configurations/organisers/Edit.vue"),

  MyProfileView: () =>
    import("@/views/main/configurations/users/MyProfile.vue"),
  EditProfileView: () =>
    import("@/views/main/configurations/users/EditProfile.vue"),

  // Abstracts
  AbstractsView: () => import("@/views/main/abstracts/Abstracts.vue"),
  AbstractView: () => import("@/views/main/abstracts/Abstract.vue"),

  // Registrations
  RegistrationsView: () => import("@/views/main/registrations/Registrations.vue"),

  // Attendance Confirmation (admin)
  AttendanceConfirmationView: () => import("@/views/main/attendance/AttendanceConfirmation.vue"),

  // My Account
  MyDashboardView: () => import("@/views/my_account/MyDashboard.vue"),
  MyEventsAccountView: () => import("@/views/my_account/MyEvents.vue"),
  MyAbstractsAccountView: () => import("@/views/my_account/MyAbstracts.vue"),
  MyAccountProfileView: () => import("@/views/my_account/MyProfile.vue"),

  // Abstract Submission (public/web)
  AbstractSubmissionView: () => import("@/views/web/AbstractSubmission.vue"),

  // Contact page
  ContactView: () => import("@/views/web/Contact.vue"),
};

// Define your route configurations
const routes = [
  {
    path: "/",
    component: routeComponents.WebLayout,
    children: [
      {
        path: "/",
        name: "Home",
        component: routeComponents.HomeView,
        props: true,
      },
      {
        path: "/login",
        name: "Login",
        component: routeComponents.LoginView,
      },
      {
        path: "/register",
        name: "Register",
        component: routeComponents.RegisterView,
      },
      {
        path: "/reset-password",
        name: "ResetPassword",
        component: routeComponents.ResetPasswordView,
      },
      {
        path: "/web-events",
        name: "WebEvents",
        component: routeComponents.WebEventsView,
      },
      {
        path: "/web-event/:id",
        name: "WebEvent",
        component: routeComponents.WebEventView,
      },
      {
        path: "/user-event-status/:userId/:eventId",
        name: "UserEventStatus",
        component: routeComponents.UserEventStatusView,
      },
      {
        path: "/attendance/:eventId/",
        name: "Attendance",
        component: routeComponents.AttendanceView,
      },
      {
        path: "/abstract-submission/:eventId",
        name: "AbstractSubmission",
        component: routeComponents.AbstractSubmissionView,
        meta: { requiresAuth: true },
      },
      {
        path: "/contact",
        name: "Contact",
        component: routeComponents.ContactView,
      },
      {
        path: "/register/:id",
        name: "EventRegister",
        component: routeComponents.EventRegisterView,
      },
      {
        path: "/payment/:event_id/:registration_id",
        name: "Payment",
        component: routeComponents.PaymentView,
      },
    ],
  },
  {
    path: "/",
    name: "Main",
    component: routeComponents.MainLayout,
    meta: { requiresAuth: true },
    children: [
      {
        path: "/dashboard",
        name: "Dashboard",
        component: routeComponents.DashboardView,
        meta: { requiresAuth: true },
      },

      {
        path: "/events",
        name: "Events",
        component: routeComponents.EventsView,
      },

      {
        path: "/add-event",
        name: "AddEvent",
        component: routeComponents.AddEventView,
      },

      {
        path: "/event/:id",
        name: "Event",
        component: routeComponents.EventView,
      },

      {
        path: "/edit-event/:id",
        name: "EditEvent",
        component: routeComponents.EditEventView,
      },

      {
        path: "/access-event/:id",
        name: "AccessEvent",
        component: routeComponents.AccessEventView,
      },

      {
        path: "/participants",
        name: "Participants",
        component: routeComponents.ParticipantsView,
      },

      {
        path: "/add-participant",
        name: "AddParticipant",
        component: routeComponents.AddParticipantView,
      },

      {
        path: "/participant/:id",
        name: "Participant",
        component: routeComponents.ParticipantView,
      },

      {
        path: "/edit-participant/:id",
        name: "EditParticipant",
        component: routeComponents.EditParticipantView,
      },

      {
        path: "/users",
        name: "Users",
        component: routeComponents.UsersView,
      },

      {
        path: "/add-user",
        name: "AddUser",
        component: routeComponents.AddUserView,
      },

      {
        path: "/user/:id",
        name: "User",
        component: routeComponents.UserView,
      },

      {
        path: "/my-profile/:id",
        name: "MyProfile",
        component: routeComponents.MyProfileView,
      },

      {
        path: "/edit-profile/:id",
        name: "EditProfile",
        component: routeComponents.EditProfileView,
      },

      {
        path: "/edit-user/:id",
        name: "EditUser",
        component: routeComponents.EditUserView,
      },

      {
        path: "/roles",
        name: "Roles",
        component: routeComponents.RolesView,
      },

      {
        path: "/add-role",
        name: "AddRole",
        component: routeComponents.AddRoleView,
      },

      {
        path: "/role/:id",
        name: "Role",
        component: routeComponents.RoleView,
      },

      {
        path: "/edit-role/:id",
        name: "EditRole",
        component: routeComponents.EditRoleView,
      },

      {
        path: "/configurations",
        name: "Configurations",
        component: routeComponents.ConfigurationsView,
      },

      {
        path: "/email-templates",
        name: "EmailTemplates",
        component: routeComponents.EmailTemplatesView,
      },

      {
        path: "/contacts",
        name: "Contacts",
        component: routeComponents.ContactsView,
      },

      {
        path: "/event-types",
        name: "EventTypes",
        component: routeComponents.EventTypesView,
      },

      {
        path: "/add-event-type",
        name: "AddEventType",
        component: routeComponents.AddEventTypeView,
      },

      {
        path: "/edit-event-type/:id",
        name: "EditEventType",
        component: routeComponents.EditEventTypeView,
      },

      {
        path: "/organisers",
        name: "Organisers",
        component: routeComponents.OrganisersView,
      },

      {
        path: "/add-organiser",
        name: "AddOrganiser",
        component: routeComponents.AddOrganiserView,
      },

      {
        path: "/edit-organiser/:id",
        name: "EditOrganiser",
        component: routeComponents.EditOrganiserView,
      },

      {
        path: "/abstracts",
        name: "Abstracts",
        component: routeComponents.AbstractsView,
      },

      {
        path: "/abstract/:id",
        name: "Abstract",
        component: routeComponents.AbstractView,
      },

      {
        path: "/registrations",
        name: "Registrations",
        component: routeComponents.RegistrationsView,
      },

      {
        path: "/attendance-confirmation",
        name: "AttendanceConfirmation",
        component: routeComponents.AttendanceConfirmationView,
      },
    ],
  },
  {
    path: "/my-account",
    component: routeComponents.MyAccountLayout,
    meta: { requiresAuth: true },
    children: [
      {
        path: "",
        name: "MyDashboard",
        component: routeComponents.MyDashboardView,
        meta: { requiresAuth: true },
      },
      {
        path: "events",
        name: "MyEvents",
        component: routeComponents.MyEventsAccountView,
        meta: { requiresAuth: true },
      },
      {
        path: "abstracts",
        name: "MyAbstracts",
        component: routeComponents.MyAbstractsAccountView,
        meta: { requiresAuth: true },
      },
      {
        path: "profile",
        name: "MyAccountProfile",
        component: routeComponents.MyAccountProfileView,
        meta: { requiresAuth: true },
      },
    ],
  },
  { path: "/:catchAll(.*)", name: "NotFound", component: NotFoundView },
];

// Create the router instance
const router = createRouter({
  history: createWebHashHistory(import.meta.env.BASE_URL),
  routes,
});

// Navigation guard: redirect to /login if route requires auth and no token
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore();
  if (to.meta.requiresAuth && !authStore.accessToken) {
    next({ name: "Login" });
  } else {
    next();
  }
});

export default router;
