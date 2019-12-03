CC=pgcc
SRCS=jacobi.c laplace2d.c
FLAGS=-fast

#serial produced files
SEQ_OBJS=$(subst .c,_seq.o,$(SRCS))
SEQ_BINS=seq

#multicore produced files
MULTI_OBJS=$(subst .c,_multi.o,$(SRCS))
MULTI_BINS=multi
MULTI_TA=multicore

#gpu produced files
GPU_OBJS=$(subst .c,_gpu.o,$(SRCS))
GPU_BINS=gpu
GPU_TA=tesla:cc60

#all produced files
OBJS=$(SEQ_OBJS) $(MULTI_OBJS) $(GPU_OBJS)
BINS=$(SEQ_BINS) $(MULTI_BINS) $(GPU_BINS)

.DUMMY:all
all:$(BINS)

#rules to build executables
seq: $(SEQ_OBJS)
	$(CC) $(FLAGS) $^ -o $@

multi: $(MULTI_OBJS)
	$(CC) $(FLAGS) -Minfo=accel -ta=$(MULTI_TA) $^ -o $@

gpu: $(GPU_OBJS)
	$(CC) $(FLAGS) -Minfo=accel -ta=$(GPU_TA) $^ -o $@


#rules to build object files
$(SEQ_OBJS): %_seq.o: %.c
	$(CC) $(FLAGS) -c $^ -o $@

$(MULTI_OBJS): %_multi.o: %.c
	$(CC) $(FLAGS) -Minfo=accel -ta=$(MULTI_TA) -o $@ -c $^

$(GPU_OBJS): %_gpu.o: %.c
	$(CC) $(FLAGS) -Minfo=accel -ta=$(GPU_TA) -o $@ -c $^


.DUMMY:clean
clean:
	rm $(OBJS) $(BINS)
