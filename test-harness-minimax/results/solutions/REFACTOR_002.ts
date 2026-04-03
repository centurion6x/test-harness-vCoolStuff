type Permission = 'read' | 'write' | 'delete' | 'manage_users';

const permissionMap: Record<string, Permission[]> = {
  admin: ['read', 'write', 'delete', 'manage_users'],
  editor: ['read', 'write'],
  viewer: ['read'],
  moderator: ['read', 'write', 'delete'],
};

function getPermissions(role: string): Permission[] {
  return permissionMap[role] ?? [];
}
