package data

// Retriever is the interface for data retrievers.
type Retriever interface {
	// Get retrieves the JSON color data associated with the given URL.
	Get(url string) ([]byte, error)
}
