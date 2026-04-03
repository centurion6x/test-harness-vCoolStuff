import { useState, useEffect } from 'react';

function useFetchUser(userId: string) {
  const [user, setUser] = useState(null);

  useEffect(() => {
    const controller = new AbortController();
    const signal = controller.signal;

    fetch(`/api/users/${userId}`, { signal })
      .then(res => res.json())
      .then(data => setUser(data))
      .catch(err => {
        if (err.name !== 'AbortError') {
          throw err;
        }
      });

    return () => {
      controller.abort();
    };
  }, [userId]);

  return user;
}
