# Introduction
Firstly, as I'm sure this is the same for most of you, I was completely unfamiliar with `brainfuck` before doing this challenge, hence why I needed to learn the syntax. Thankfully, `brainfuck` is one of the more compact languages, making it fairly easy once you get the hang of it. With only eight operators at our disposale, I set out to figure out what this crackme was doing.

## Syntax overview
Well, for such a compact language, it's quite easy to list every single operator and their purpose. Huge thanks to [brainfuck introduction](https://gist.github.com/roachhd/dce54bec8ba55fb17d3a)
```js
> // moves the memory pointer to the right by 1 block
< // moves the memory pointer to the left by 1 block
+ // increases the value stored in the block (where the memory pointer is located)
- // decreases the value stored at the block (where the memory pointer is located)
[ // similar to c while (cur_block_value) != 0 loop
] // if block currently pointed to value is not zero, then jump back to [
, // similar to c getchar(), input one character 
. // like putchar() in c, output to console.
```

## Outputting "H" 
Now, characters in brainfuck are represented by ASCII codes. This can make things... quite long. Technically, you would need a memory block to have the value of 72 in one of the memory blocks just to print "H". You can do this a few ways, either... having "+" 72 times, or using their loop feature. I'm a <b>bad programmer</b>, so innately my brain craved to just do "+" 72 times, but that's not fun! :3

```bf
>++++++++++++
```

Looks confusing, right? What on earth is going on? Well, it's quite simple, really. Imagine we have a large (for the sake of simplicity, we'll use JavaScript as an example) array, and the `>` operator shifts the idx of where we are in the array by one. Then, when we're at our desired position, we increment it by 12 times (this will make sense later, I promise)

How are we going to get 72 from 12? Well, 6 * 12 is... 72! The example in the brainfuck introduction I linked above gives a more compact way of doing this, but to ensure I fully understood, I did it a different way. So now we know the logic we're trying to replicate, how do we introduce it into bf? 

```bf
>++++++++++++[<++++++>-]
```

What just happened? Why are we using brackets? Well, it's quite simple. [] In simple terms, is like a loop. It repeats whatevers contained between the brackets until the memory pointer value is zero. All this is really doing is going back to the first memory pointer, adding 6 to it, then going back to the memory pointer where our value is 12, and decreasing it. It'll repeat 12 times, since... 12 - 12 = 0, and then the loop will end. As I declared earlier, 6 * 12 = 72, right? So unless my math is bad (which it very well could be, I'd be surprised if it wasn't), this should give us the ascii code for "H" in the first memory pointer.

Let's print it and find out. How do we do that? Simple! We'll just go to where our values are stored (the first memory block/idx in the array), and do ".". It looks like this in code 

```bf
>++++++++++++[<++++++>-]<.
```

Yep! Unexpectedly, my math wasn't wrong, and it did in fact output "H"

# Writing a memory analyzer for Brainfuck
Now, it's going to get quite tedious keeping track of each value, and their ascii representative. Let's make a simple python program that analyzes the brainfuck code, and outputs a simple ascii memory block diagram.

At first it was really simple, just keep track of the memory_pointer and increment it depending on `<` or `>` usage, and add to a memory array with the memory_pointer being the idx based on `+`, but then I ran into the dreadful loops. I was close to giving up, but that wouldn't be fun. I knew I had to figure this out, I hadn't even gotten to the crackme yet. It's not like it was difficult, just tedious knowing I had already hit a hurdle and I wasn't close to the crackme.

After a losing battle with my keyboard for about 15 minutes, I figured out how to handle loops. But... what about nested loops? I needed a preprocessing loop for this.

After an additional 20 minutes (this took way longer than needed, I rewrote my implemntation three times), I was able to come up with a (what I think is) solid implementation. I'd use a stack-based approach, preprocess the code via looping through it, having a stack array, and loops dictionary. When I encounter a `[` I'll insert it to the stack, when I encounter a `]`, I'll pop from the array and make two loop dictionary entries, one with the pop'd array result, and then one with the current position.

It worked, for my program at least. That was good, I can now view memory extremely easily. You can check the source code in the "source" directory, it's within a file called memory_analyzer.py

Time to test it with other brainfuck programs! 

Excitedly, I pasted the brainfuck crackme code into my input file, and ran it through the program... it didn't output anything after 40 seconds. Oh god, what did I do wrong? I knew it couldn't be that easy. It was time to dig deeper, the whole reason I wrote the program was to be able to use it with the crackme, its cmpatibility with the crackme was <b>vital</b>

After some further debugging, I got it to work. But the memory seemed... empty, with only one index that wasn't 0, and that was 1. Surely this had to be an issue with my program? Or.. were they cleaning up the memory themselves? That would be interesting, and would be something I'd do if I ever made a brainfuck crackme.

It took a while, but I decided they were doing a memory clean up. I introduced a new snapshot system, which at vital points would take note of the code, save a copy of the memory to a dictionary with the key being the current position, and output it to a .json file.

```json
{
    "174": [
        1,
        0,
        98,
        114,
        97,
        105,
        110,
        102,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0
    ]
}
```

The extract above was taken directly from my json dump. 98, 114, 97, 105, 110, 102.. that seems interesting. After converting them to their characters, I found out that it was b, r, a, i, n, f. Is this the password? Well, I wasn't sure.

Now, let's crack the program. I wanted to produce two cracks, one which would manipulate the comparison check and make it always pass no matter what, and then one where I could produce the password myself. The latter would take a little more work than the first, so let's start with the first. 

There isn't a direct if-statement in brainfuck, but to replicate it, typically, people will have a simple 0 or 1 check. How? Well our `[]` loop only runs if there is 1 in the current memory cell/idx. If there is zero, it would skip. That's pretty much how they conduct if statements. So all I needed to do was locate the comparison, and add "+" right before they enter the loop. Technically, this would break if you inputted the right password, but who cares about that. You can find the cracked crackme in `/brainfuck/patched.bf`. 

Extracting the password would require use of our memory_analyzer file. I added a `!` command, which would print useful information when i inserted it into the code. This is useful for getting the ascii values.

After a while, I was able to find which method they were using to locate the password. First of all, they would gather your 6 input characters, and, from the bottom upward, go in a chain; - 10, + 10, - 10, + 10, and so on. However, what I noticed instantly was that they were always adding 1 or 2, or in one case subtracting 1 from it. This initially made me wonder if there even was a password, since they were adding +1 so it always went into that loop. But... then I remembered brainfuck uses % 256, meaning that if you had 255 and you added 1 to it, it becomes 0, and skips the loop. That was the method for solving it. Leaving us with two methods of a "crack", manually making the password always correct no matter what, and implementing the password: `1l0v3u`. 

This was an extremely fun challenge, and this wouldn't be possible without the crackme. I'll link it below, along with a link to the person's github that uploaded it. 

[authors github](https://github.com/0v41n)

[crackme github](https://github.com/0v41n/BrainFuck-Crackme)
