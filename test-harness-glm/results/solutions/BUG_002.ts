function useFetchUser(userId: string) {
  const [user, setUser] = useState(null);

  useEffect(() => {
    const controller = new AbortController();

    fetch(`/api/users/${userId}`, { signal: controller.signal })
      .then(res => res.json())
      .then(data => {
        if (!controller.signal.aborted) {
          setUser(data);
        }
      })
      .catch(err => {
        if (err.name !== 'AbortError') {
          throw err;
        }
      });

    return () => controller.abort();
  }, [userId]);

  return user;
}
