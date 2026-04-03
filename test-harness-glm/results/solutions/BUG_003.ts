function shouldRunToday(scheduledDateISO: string): boolean {
  const scheduled = new Date(scheduledDateISO);
  const today = new Date();
  return (
    scheduled.getFullYear() === today.getFullYear() &&
    scheduled.getMonth() === today.getMonth() &&
    scheduled.getDate() === today.getDate()
  );
}
