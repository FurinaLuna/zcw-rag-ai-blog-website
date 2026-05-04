<template>
  <div class="admin-layout flex min-h-screen bg-bg-page">
    <AdminSidebar />
    <div class="flex flex-1 flex-col lg:ml-[220px]">
      <AdminTopbar />
      <main class="flex-1 p-6">
        <slot />
      </main>
    </div>
  </div>
</template>
