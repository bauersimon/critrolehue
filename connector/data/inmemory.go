package data

// InMemory is an in-memory data retriever.
type InMemory struct {
	data map[string]string
}

// Get retrieves the JSON color data associated with the given URL.
func (r *InMemory) Get(url string) ([]byte, error) {
	return []byte(r.data[url]), nil
}

// NewInMemory creates a new in-memory data retriever.
func NewInMemory(data map[string]string) Retriever {
	return &InMemory{
		data: data,
	}
}
