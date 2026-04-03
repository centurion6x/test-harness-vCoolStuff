const permissionMap: Record<string, string[]> = {
  admin: ['read', 'write', 'delete', 'manage_users'],
  editor: ['read', 'write'],
  viewer: ['read'],
  moderator: ['read', 'write', 'delete']
};

function getPermissions(role: string): string[] {
  return permissionMap[role] || [];
}
