function getPermissions(role: string): string[] {
  const permissions: Record<string, string[]> = {
    admin: ['read', 'write', 'delete', 'manage_users'],
    editor: ['read', 'write'],
    viewer: ['read'],
    moderator: ['read', 'write', 'delete']
  };
  return permissions[role] ?? [];
}
