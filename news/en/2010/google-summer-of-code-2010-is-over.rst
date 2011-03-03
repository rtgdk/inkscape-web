Title: Google Summer of Code 2010 is over
Author: prokoudine
Category: General
Date: 2010-09-09

Google Summer of Code is over now, and we have mixed results. Unfortunately we
lost two students at midterm evaluation in July, and another student at final
evaluation in August. On the other hand, we have two very successful projects.

The first project, by Krzysztof Kosiński, was about porting the whole rendering
to Cairo, which resulted in a considerable performance boost itself. But
Krzysztof also implemented support for multiple cores/processors to use
multiple threads for rendering SVG filters. He is also planning to implement
SVG filters in OpenCL, so that rendering could be delegated to GPU where
available. The second project, by Abhishek Sharma, was about C++ification of
SPLayer and privatization of XML nodes which is also going to help parallel
processing.

The other good news is that one of the projects that failed at midterm
evaluation, PowerStroke live path effect, was picked by the student's mentor,
Johan Engelen. Initial implementation is already available in development tree,
but currently disabled by default. It is quite possible that this LPE will be
available in 0.49, as well as both successful GSoC projects.
