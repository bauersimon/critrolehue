package pulse

// Timestamper is a type that gives the current timestamp of some medium.
type Timestamper interface {
	// Done returns true if the content is done.
	Done() bool
	// Timestamp is the current timestamp in seconds.
	Timestamp() float64
}
