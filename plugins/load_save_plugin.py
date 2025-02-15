
import de, cPickle


def save_dsmp(file_name, row_count, arg_count, data, markers, args, targets):
        print "Saving dsmp: ", file_name
        info =  {
                  "arg_count": arg_count,
                  "row_count": row_count,
                  "targets": targets,
                  "arguments": args,
                  "markers": markers,
                  "data": data
                }
        f = open(file_name, "wb")
        f.write(cPickle.dumps(info, 1))
        f.close()
        print "saved..."

def load_dsmp(file_name):
        print "loading dsmp: ", file_name
        f = open(file_name, "rb")
        info = cPickle.loads(f.read())
        f.close()
        arguments = info["arguments"]
        markers = info["markers"]
        targets = info["targets"]
        data = info["data"]
        i = 0
        for argument in arguments:
          de.add_argument(argument)
          if i in targets:
            de.set_is_target(i, 1)
          i += 1
        de.set_row_count(info["row_count"])
        i = 0
        for marker in markers:
          de.set_row_marker(i, marker)
          i += 1
        r = 0
        for row in data:
          c = 0
          for col in row:
            de.set_cell(r, c, col)
            c += 1
          r += 1
        print "loaded..."


        

def save_indn(file_name, net):
        print "Saving inductive net: ", file_name
        data = cPickle.dumps(net, 1)
        f = open(file_name, "wb")
        f.write(data)
        f.close()
        print "Saved..."

def load_indn(file_name):
        f = open(file_name, "rb")
        net = cPickle.loads(f.read())
        f.close()
        return net
        
