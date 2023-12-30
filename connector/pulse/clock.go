package pulse

import "time"

// Clock is a Timestamper that generates timestamps accoring to the real time.
type Clock struct {
	start  time.Time
	offset float64
}

// Done always returns false.
func (c *Clock) Done() bool {
	return false
}

// Timestamp returns the time elapsed since the clock was started.
func (c *Clock) Timestamp() float64 {
	return time.Since(c.start).Seconds() + c.offset
}

func NewClock(offset float64) Timestamper {
	return &Clock{
		start:  time.Now(),
		offset: offset,
	}
}
