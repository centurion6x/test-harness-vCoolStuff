import { useState, useEffect } from 'react';

function useFetchUser(userId: string) {
  const [user, setUser] = useState(null);

  useEffect(() => {
    let cancelled = false;

    fetch(`/api/users/${userId}`)
      .then(res => res.json())
      .then(data => {
        if (!cancelled) {
          setUser(data);
        }
      });

    return () => {
      cancelled = true;
    };
  }, [userId]);

  return user;
}
